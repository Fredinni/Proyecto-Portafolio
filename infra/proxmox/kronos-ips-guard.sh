#!/bin/sh
# pfSense/FreeBSD only. The native alias and its scoped floating rules must
# already exist. This controller never installs rules or creates PF tables.
# A supervised failure is bounded recovery, not a promise of instant fail-close.
set -u
umask 077

SELF=/usr/local/sbin/kronos-ips-guard
TABLE=KRONOS_IPS_GUARD
CLOSED=/usr/local/etc/kronos-ips-guard.closed
HEALTH=/usr/local/sbin/kronos-ips-status
MGMT_STATES=/usr/local/sbin/kronos-guard-mgmt-states
HOLD=/var/run/kronos-ips-guard.hold
CHILD=/var/run/kronos-ips-guard.worker.pid
SUPERVISOR=/var/run/kronos-ips-guard.supervisor.pid
LOCK=/var/run/kronos-ips-guard.lock
SHUTDOWN_RELEASE=/var/run/kronos-ips-guard.shutdown-release
TIMEOUT=/usr/bin/timeout
[ -x "$TIMEOUT" ] || TIMEOUT=/bin/timeout

note() { /usr/bin/logger -t kronos-ips-guard -- "$*"; }
error() { echo "kronos-ips-guard: $*" >&2; note "$*"; }
native_table() {
    "$TIMEOUT" 3 /sbin/pfctl -s Tables 2>/dev/null | /usr/bin/grep -Fxq "$TABLE"
}
validate_closed() {
    [ -r "$CLOSED" ] && [ "$(/bin/cat "$CLOSED")" = '0.0.0.0/0' ]
}
close_guard() {
    native_table && validate_closed || {
        error 'Native table or closed-address file missing/invalid; no table created.'
        return 1
    }
    "$TIMEOUT" 3 /sbin/pfctl -t "$TABLE" -T replace -f "$CLOSED" >/dev/null 2>&1 || {
        error 'Failed to close the native guard table.'; return 1;
    }
}
open_guard() {
    [ ! -e "$HOLD" ] || return 2
    native_table || return 1
    "$TIMEOUT" 3 /sbin/pfctl -t "$TABLE" -T flush >/dev/null 2>&1 || return 1
    # A concurrent administrative hold wins even if it arrived during PF I/O.
    [ ! -e "$HOLD" ] || { close_guard; return 2; }
}
purge_project_states() {
    # Never flush the state table. Purge CORP/DMZ/VOIP prefixes, then delegate
    # selective VLAN99 cleanup to the scoped helper preserving administration
    # and Tailscale. Production networks are never selected here.
    for network in 192.168.10.0/24 192.168.20.0/24 192.168.30.0/24; do
        "$TIMEOUT" 3 /sbin/pfctl -k "$network" >/dev/null 2>&1 || return 1
        "$TIMEOUT" 3 /sbin/pfctl -k 0.0.0.0/0 -k "$network" >/dev/null 2>&1 || return 1
    done
    [ -x "$MGMT_STATES" ] || {
        error 'Selective MGMT state helper missing; guard remains closed.'
        return 1
    }
    "$TIMEOUT" 5 "$MGMT_STATES" >/dev/null 2>&1 || {
        error 'Selective MGMT state cleanup failed; guard remains closed.'
        return 1
    }
}
readiness() { "$TIMEOUT" 3 "$HEALTH" >/dev/null 2>&1; }
verified_pid() {
    file=$1; kind=$2
    [ -r "$file" ] || return 1
    candidate=$(/bin/cat "$file")
    case "$candidate" in ''|*[!0-9]*) return 1;; esac
    [ "$candidate" -gt 1 ] || return 1
    command=$(/bin/ps -p "$candidate" -o command= 2>/dev/null) || return 1
    case "$kind:$command" in
        supervisor:*daemon*"$SELF"*) ;;
        worker:*"$SELF worker"*) ;;
        *) return 1;;
    esac
    printf '%s\n' "$candidate"
}
worker_exit() {
    trap - EXIT TERM INT HUP
    close_guard && purge_project_states || error 'Exit close/purge incomplete; operator intervention required.'
    note 'Worker exited; guard closure requested.'
}
worker() {
    trap worker_exit EXIT
    trap 'exit 1' TERM INT HUP
    close_guard || exit 1
    purge_project_states || { error 'Initial scoped state purge failed.'; exit 1; }
    state=closed
    note 'Guard closed at worker startup.'
    while :; do
        # daemon supervises its child, not itself. An orphan must never keep
        # reopening the guard after its supervising process disappears.
        if ! verified_pid "$SUPERVISOR" supervisor >/dev/null; then
            error 'Supervisor absent/unverified; closing orphaned worker.'
            close_guard || exit 1
            purge_project_states || exit 1
            exit 1
        fi
        if [ ! -e "$HOLD" ] && readiness; then
            # Also reopens a boot-closed alias after a native filter reload.
            if ! open_guard; then
                close_guard || exit 1
                if [ ! -e "$HOLD" ]; then
                    error 'Opening failed; exiting with closure.'; exit 1
                fi
                if [ "$state" != closed ]; then
                    purge_project_states || exit 1
                    state=closed
                    note 'Guard closed by concurrent administrative hold.'
                fi
            elif [ "$state" != open ]; then
                state=open
                note 'Guard open: both IPS sensors passed readiness.'
            fi
        elif [ "$state" != closed ]; then
            close_guard || exit 1
            state=closed
            purge_project_states || { error 'Scoped state purge failed.'; exit 1; }
            note 'Guard closed: hold or IPS readiness failure.'
        else
            # Refresh an already closed native alias after external filter reloads.
            close_guard || exit 1
        fi
        /bin/sleep 1
    done
}
start_locked() {
    if pid=$(verified_pid "$SUPERVISOR" supervisor); then
        echo "Guard supervisor already running: $pid"; return 0
    fi
    if pid=$(verified_pid "$CHILD" worker); then
        error "Unsupervised worker $pid exists; refusing duplicate start."; return 1
    fi
    close_guard || return 1
    purge_project_states || return 1
    # Output goes to syslog through logger, with transition-only worker messages.
    /usr/sbin/daemon -r -R 1 -p "$CHILD" -P "$SUPERVISOR" \
        "$SELF" worker </dev/null >/dev/null 2>&1 || return 1
    /bin/sleep 1
    verified_pid "$SUPERVISOR" supervisor >/dev/null || {
        close_guard; error 'Supervisor did not start.'; return 1;
    }
    echo 'Guard supervisor started; readiness controls reopening.'
}
stop_guard() {
    # Hold persists across restart until an explicit resume operation.
    /bin/rm -f "$SHUTDOWN_RELEASE" || return 1
    : > "$HOLD" || return 1
    close_guard || return 1
    purge_project_states || return 1
    parent=$(verified_pid "$SUPERVISOR" supervisor || true)
    child=$(verified_pid "$CHILD" worker || true)
    [ -z "$parent" ] || /bin/kill -TERM "$parent" || return 1
    [ -z "$child" ] || /bin/kill -TERM "$child" 2>/dev/null || true
    # Bounded wait; never signal an unverified/reused PID.
    n=0
    while [ "$n" -lt 12 ]; do
        if ! verified_pid "$SUPERVISOR" supervisor >/dev/null && \
           ! verified_pid "$CHILD" worker >/dev/null; then
            close_guard || return 1
            echo 'Guard stopped and held closed.'; return 0
        fi
        /bin/sleep 1; n=$((n + 1))
    done
    close_guard
    error 'Verified processes still running after bounded stop; guard held closed.'
    return 1
}
guard_status() {
    result=0
    if pid=$(verified_pid "$SUPERVISOR" supervisor); then
        echo "Supervisor: $pid"
    else
        echo 'Supervisor: stopped/unverified'; result=1
    fi
    if pid=$(verified_pid "$CHILD" worker); then
        echo "Worker: $pid"
    else
        echo 'Worker: stopped/unverified'; result=1
    fi
    if [ -e "$HOLD" ]; then
        echo 'Hold: active (forwarding intentionally held closed)'; result=1
    else
        echo 'Hold: inactive'
    fi
    if readiness; then
        echo 'IPS readiness: PASS'
    else
        echo 'IPS readiness: FAIL'; result=1
    fi
    if ! native_table; then
        echo 'Guard table: MISSING/UNREADABLE'
        error 'Native guard table missing or table query failed.'
        result=1
    elif contents=$("$TIMEOUT" 3 /sbin/pfctl -t "$TABLE" -T show 2>/dev/null); then
        if [ -z "$contents" ]; then
            echo 'Guard table: OPEN (empty)'
        else
            echo 'Guard table: CLOSED/NONEMPTY'
            printf '%s\n' "$contents"
            result=1
        fi
    else
        echo 'Guard table: QUERY FAILED'; result=1
    fi
    if [ "$result" -eq 0 ]; then
        echo 'Guard operational status: READY'
    else
        echo 'Guard operational status: NOT READY'
    fi
    return "$result"
}

[ "$(/usr/bin/id -u)" -eq 0 ] || { echo 'Requires root.' >&2; exit 1; }
case "${1:-status}" in
    boot-start)
        /usr/bin/lockf -t 0 "$LOCK" "$SELF" boot-start-locked ;;
    boot-start-locked)
        start_locked || exit 1
        # Release only the hold introduced by our shutdown hook. An operator's
        # pre-existing hold remains closed across reboot.
        if [ -e "$SHUTDOWN_RELEASE" ]; then
            /bin/rm -f "$HOLD" "$SHUTDOWN_RELEASE" || exit 1
        fi ;;
    start) /usr/bin/lockf -t 0 "$LOCK" "$SELF" start-locked ;;
    start-locked) start_locked ;;
    worker) worker ;;
    stop) /usr/bin/lockf -t 0 "$LOCK" "$SELF" stop-locked ;;
    stop-locked) stop_guard ;;
    hold) /usr/bin/lockf -t 0 "$LOCK" "$SELF" hold-locked ;;
    hold-locked)
        /bin/rm -f "$SHUTDOWN_RELEASE" || exit 1
        : > "$HOLD" && close_guard && purge_project_states &&
            echo 'Guard held closed; explicit resume required.' ;;
    shutdown-hold) /usr/bin/lockf -t 30 "$LOCK" "$SELF" shutdown-hold-locked ;;
    shutdown-hold-locked)
        original_hold=no
        [ ! -e "$HOLD" ] || original_hold=yes
        : > "$HOLD" && close_guard && purge_project_states || exit 1
        if [ "$original_hold" = no ]; then
            : > "$SHUTDOWN_RELEASE" || exit 1
        else
            /bin/rm -f "$SHUTDOWN_RELEASE" || exit 1
        fi
        echo 'Guard held closed before shutdown.' ;;
    resume) /usr/bin/lockf -t 0 "$LOCK" "$SELF" resume-locked ;;
    resume-locked)
        # Resuming never opens directly: the supervised worker verifies readiness.
        verified_pid "$SUPERVISOR" supervisor >/dev/null &&
            /bin/rm -f "$HOLD" "$SHUTDOWN_RELEASE" && echo 'Hold removed; worker will verify IPS readiness.' ;;
    status) guard_status ;;
    *) echo "Usage: $SELF {boot-start|start|stop|hold|shutdown-hold|resume|status}" >&2; exit 2 ;;
esac
