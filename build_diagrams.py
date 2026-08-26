import os

def create_pfctl_decision_flow():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 750" width="100%" height="100%">
  <defs>
    <radialGradient id="bgGrad" cx="50%" cy="50%" r="80%">
      <stop offset="0%" stop-color="#0C1626" />
      <stop offset="60%" stop-color="#060B14" />
      <stop offset="100%" stop-color="#020408" />
    </radialGradient>

    <linearGradient id="stepHeaderBlue" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284C7" />
      <stop offset="100%" stop-color="#0369A1" />
    </linearGradient>
    <linearGradient id="stepHeaderAmber" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#D97706" />
      <stop offset="100%" stop-color="#B45309" />
    </linearGradient>
    <linearGradient id="stepHeaderCrimson" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#E11D48" />
      <stop offset="100%" stop-color="#BE123C" />
    </linearGradient>
    <linearGradient id="stepHeaderEmerald" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#059669" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>

    <!-- Filters -->
    <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <filter id="glowAmber" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <filter id="glowRed" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Grid -->
    <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1E293B" stroke-width="0.6" stroke-opacity="0.4" />
    </pattern>

    <!-- Markers -->
    <marker id="arrowCyan" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
      <polygon points="0 0, 8 3.5, 0 7" fill="#00F5FF" />
    </marker>
    <marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
      <polygon points="0 0, 8 3.5, 0 7" fill="#F59E0B" />
    </marker>
    <marker id="arrowRed" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
      <polygon points="0 0, 8 3.5, 0 7" fill="#FF1E56" />
    </marker>
    <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
      <polygon points="0 0, 8 3.5, 0 7" fill="#10B981" />
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1300" height="750" fill="url(#bgGrad)" />
  <rect width="1300" height="750" fill="url(#grid)" />

  <!-- Frame -->
  <rect x="20" y="20" width="1260" height="710" rx="12" fill="none" stroke="#1E293B" stroke-width="1.5" />
  <rect x="24" y="24" width="1252" height="702" rx="10" fill="none" stroke="#00F5FF" stroke-width="0.7" stroke-opacity="0.3" stroke-dasharray="30 60" />

  <!-- ================= BANNER TITLE ================= -->
  <g transform="translate(650, 52)">
    <text x="0" y="0" font-family="'Orbitron', 'Segoe UI', sans-serif" font-size="24" font-weight="900" 
          letter-spacing="5" fill="#FFFFFF" text-anchor="middle">
      MOTOR pfctl : FILTRADO DE FALSOS POSITIVOS Y VERIFICACI&#211;N EN KERNEL
    </text>
    <text x="0" y="24" font-family="'Consolas', monospace" font-size="13" font-weight="bold" 
          letter-spacing="2" fill="#00F5FF" text-anchor="middle" filter="url(#glowCyan)">
      DIAGRAMA TE&#211;RICO DE PROCESAMIENTO &#8226; SUPRESI&#211;N &gt;50% DE RUIDO &#8226; VALIDACI&#211;N AT&#211;MICA
    </text>
  </g>
  <line x1="60" y1="86" x2="1240" y2="86" stroke="#1E293B" stroke-width="2" />
  <line x1="420" y1="86" x2="880" y2="86" stroke="#00F5FF" stroke-width="2.5" filter="url(#glowCyan)" />

  <!-- ================= STAGE 1: INGESTION ================= -->
  <g transform="translate(60, 115)">
    <rect width="340" height="240" rx="10" fill="#0B1526" stroke="#00F5FF" stroke-width="2" filter="url(#glowCyan)" />
    <path d="M 0 10 Q 0 0 10 0 L 330 0 Q 340 0 340 10 L 340 38 L 0 38 Z" fill="url(#stepHeaderBlue)" />
    <text x="170" y="25" font-family="'Orbitron', sans-serif" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">FASE 1: INGESTA &amp; RING BUFFER</text>

    <text x="16" y="68" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#00F5FF">1. Netmap Inline IPS (Suricata 7.x)</text>
    <text x="28" y="88" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">Inspecci&#243;n de paquetes en ring-buffer directo</text>

    <text x="16" y="118" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#38BDF8">2. Generaci&#243;n de Eventos EVE JSON</text>
    <text x="28" y="138" font-family="'Consolas', monospace" font-size="12" fill="#94A3B8">/var/log/suricata/eve.json</text>

    <text x="16" y="168" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#E2E8F0">3. Captura en Tiempo Real (Tailing)</text>
    <text x="28" y="188" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#94A3B8">I/O as&#237;ncrono sin bloqueo de red</text>

    <rect x="16" y="202" width="308" height="24" rx="4" fill="#041B2D" stroke="#00F5FF" stroke-width="1" />
    <text x="170" y="219" font-family="'Consolas', monospace" font-size="11.5" font-weight="bold" fill="#34D399" text-anchor="middle">LATENCIA INFERIOR A 10ms</text>
  </g>

  <!-- Arrow Stage 1 -> Stage 2 -->
  <path d="M 400 235 L 480 235" stroke="#00F5FF" stroke-width="3.5" fill="none" marker-end="url(#arrowCyan)" filter="url(#glowCyan)" />
  <text x="440" y="222" font-family="'Consolas', monospace" font-size="11" font-weight="bold" fill="#00F5FF" text-anchor="middle">EVENT STREAM</text>

  <!-- ================= STAGE 2: HEURISTIC CORRELATOR ================= -->
  <g transform="translate(480, 105)">
    <rect width="380" height="260" rx="10" fill="#1A1406" stroke="#F59E0B" stroke-width="2" filter="url(#glowAmber)" />
    <path d="M 0 10 Q 0 0 10 0 L 370 0 Q 380 0 380 10 L 380 38 L 0 38 Z" fill="url(#stepHeaderAmber)" />
    <text x="190" y="25" font-family="'Orbitron', sans-serif" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">FASE 2: AN&#193;LISIS HEUR&#205;STICO KRONOS</text>

    <text x="16" y="68" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#FBBF24">1. Parser de Payload SQLi / RCE</text>
    <text x="28" y="88" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">Evaluaci&#243;n de sintaxis: UNION, OR '1'='1, SLEEP()</text>

    <text x="16" y="116" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#FBBF24">2. C&#225;lculo de Score de Confianza</text>
    <text x="28" y="136" font-family="'Consolas', monospace" font-size="12" fill="#94A3B8">Confidence = W_sig * Score + W_geo * GeoScore</text>

    <text x="16" y="164" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#FBBF24">3. Filtro de Supresi&#243;n de Ruido</text>
    <text x="28" y="184" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">Detecci&#243;n de escaneos masivos (ZGrab, Shodan, Nmap)</text>

    <!-- Branch Indicator Box -->
    <rect x="16" y="200" width="348" height="44" rx="5" fill="#2A1803" stroke="#F59E0B" stroke-width="1.5" />
    <text x="190" y="218" font-family="'Consolas', monospace" font-size="11" font-weight="bold" fill="#FDE68A" text-anchor="middle">¿SCORE &gt;= 0.75 Y VECTOR CR&#205;TICO?</text>
    <text x="190" y="234" font-family="'Consolas', monospace" font-size="10.5" fill="#FFFFFF" text-anchor="middle">[ S&#205; &#8594; VALIDAR KERNEL ] | [ NO &#8594; DESCARTAR ]</text>
  </g>

  <!-- Split Paths: Top Right (Noise Elimination) & Down (Kernel Validation) -->

  <!-- Path to Noise Elimination (Right) -->
  <path d="M 860 190 L 940 190" stroke="#FF1E56" stroke-width="3" stroke-dasharray="5 4" fill="none" marker-end="url(#arrowRed)" />
  <text x="900" y="180" font-family="'Consolas', monospace" font-size="11" font-weight="bold" fill="#FF1E56" text-anchor="middle">NO (RUIDO)</text>

  <!-- ================= NOISE ELIMINATION BOX ================= -->
  <g transform="translate(940, 115)">
    <rect width="300" height="240" rx="10" fill="#200810" stroke="#FF1E56" stroke-width="2" filter="url(#glowRed)" />
    <path d="M 0 10 Q 0 0 10 0 L 290 0 Q 300 0 300 10 L 300 38 L 0 38 Z" fill="url(#stepHeaderCrimson)" />
    <text x="150" y="25" font-family="'Orbitron', sans-serif" font-size="13.5" font-weight="bold" fill="#FFFFFF" text-anchor="middle">SUPRESI&#211;N DE FALSOS POSITIVOS</text>

    <text x="16" y="68" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#FF809B">&#10008; Descarte Silencioso</text>
    <text x="28" y="88" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">Escaneos autom&#225;ticos de puertos</text>
    <text x="28" y="108" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">Peticiones 404 de crawlers web</text>

    <text x="16" y="138" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#FF809B">&#10008; Cero Fatiga de Alerta</text>
    <text x="28" y="158" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">No se llama al CISO innecesariamente</text>

    <rect x="16" y="182" width="268" height="40" rx="5" fill="#380A18" stroke="#FF1E56" stroke-width="1.2" />
    <text x="150" y="200" font-family="'Consolas', monospace" font-size="11" font-weight="bold" fill="#FDA4AF" text-anchor="middle">&gt;50% DE ALERTAS PURGADAS</text>
    <text x="150" y="214" font-family="'Consolas', monospace" font-size="10" fill="#FFFFFF" text-anchor="middle">Registro local en log_correlator.log</text>
  </g>

  <!-- Down Path from Heuristic to Kernel Validation (Stage 3) -->
  <path d="M 670 365 L 670 435" stroke="#10B981" stroke-width="3.5" fill="none" marker-end="url(#arrowGreen)" />
  <text x="730" y="400" font-family="'Consolas', monospace" font-size="12" font-weight="bold" fill="#10B981" text-anchor="middle">S&#205; (SCORE &gt;= 0.75)</text>

  <!-- ================= STAGE 3: KERNEL VERIFICATION (pfctl) ================= -->
  <g transform="translate(380, 440)">
    <rect width="580" height="250" rx="10" fill="#051B14" stroke="#10B981" stroke-width="2" />
    <path d="M 0 10 Q 0 0 10 0 L 570 0 Q 580 0 580 10 L 580 38 L 0 38 Z" fill="url(#stepHeaderEmerald)" />
    <text x="290" y="25" font-family="'Orbitron', sans-serif" font-size="14.5" font-weight="bold" fill="#FFFFFF" text-anchor="middle">FASE 3: VERIFICACI&#211;N AT&#211;MICA EN KERNEL pfctl (FreeBSD)</text>

    <!-- Submodules in 2 columns -->
    <g transform="translate(16, 55)">
      <text x="0" y="16" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#34D399">1. Test de Kernel FreeBSD</text>
      <text x="12" y="36" font-family="'Consolas', monospace" font-size="12" fill="#A7F3D0">pfctl -t snort2c -T test &lt;IP&gt;</text>
      <text x="12" y="54" font-family="'Segoe UI', sans-serif" font-size="12" fill="#94A3B8">Retorno 0 = IP bloqueada en hardware</text>

      <text x="0" y="82" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#34D399">2. Purga de Estados TCP (Kill)</text>
      <text x="12" y="102" font-family="'Consolas', monospace" font-size="12" fill="#A7F3D0">pfctl -k &lt;IP&gt; &amp;&amp; pfctl -k 0/0 -k &lt;IP&gt;</text>
      <text x="12" y="120" font-family="'Segoe UI', sans-serif" font-size="12" fill="#94A3B8">Cierre de sockets activos del atacante</text>
    </g>

    <g transform="translate(300, 55)">
      <text x="0" y="16" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#34D399">3. Inserci&#243;n Forzada de Emergencia</text>
      <text x="12" y="36" font-family="'Consolas', monospace" font-size="12" fill="#A7F3D0">pfctl -t snort2c -T add &lt;IP&gt;</text>
      <text x="12" y="54" font-family="'Segoe UI', sans-serif" font-size="12" fill="#94A3B8">Garantiza contenci&#243;n perimetral 100%</text>

      <text x="0" y="82" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#38BDF8">4. Formateo de Payload JSON SOAR</text>
      <text x="12" y="102" font-family="'Segoe UI', sans-serif" font-size="12" fill="#CBD5E1">IP, Pa&#237;s, Vector SQLi, Hora, Regla SID</text>
    </g>

    <!-- Final Trigger Bar -->
    <rect x="16" y="190" width="548" height="44" rx="6" fill="#022618" stroke="#10B981" stroke-width="1.5" />
    <text x="290" y="210" font-family="'Consolas', monospace" font-size="12" font-weight="bold" fill="#6EE7B7" text-anchor="middle">ATAQUE REAL CONFIRMADO Y NEUTRALIZADO EN KERNEL</text>
    <text x="290" y="226" font-family="'Consolas', monospace" font-size="11" font-weight="bold" fill="#00F5FF" text-anchor="middle">&#8680; DISPARO DE LLAMADA TELEF&#211;NICA DE ALERTA AL CISO (PUERTO 5000 /webhook)</text>
  </g>

  <!-- Final Exit Arrow to AI Voice Agent -->
  <path d="M 960 565 L 1050 565" stroke="#00F5FF" stroke-width="3.5" fill="none" marker-end="url(#arrowCyan)" filter="url(#glowCyan)" />
  <text x="1005" y="552" font-family="'Consolas', monospace" font-size="11" font-weight="bold" fill="#00F5FF" text-anchor="middle">VOICE SOAR</text>

  <!-- Output Box: Trigger SOAR -->
  <g transform="translate(1050, 485)">
    <rect width="190" height="160" rx="10" fill="#1B0C2E" stroke="#A855F7" stroke-width="2" />
    <path d="M 0 10 Q 0 0 10 0 L 180 0 Q 190 0 190 10 L 190 35 L 0 35 Z" fill="#6B21A8" />
    <text x="95" y="23" font-family="'Orbitron', sans-serif" font-size="13" font-weight="bold" fill="#FFFFFF" text-anchor="middle">AGENTE DE VOZ IA</text>

    <text x="14" y="60" font-family="'Segoe UI', sans-serif" font-size="13" font-weight="bold" fill="#D8B4FE">Llamada Activa:</text>
    <text x="14" y="80" font-family="'Consolas', monospace" font-size="11.5" fill="#FFFFFF">Asterisk PBX</text>
    <text x="14" y="98" font-family="'Consolas', monospace" font-size="11.5" fill="#00F5FF">Gemini Live 3.1</text>
    <text x="14" y="120" font-family="'Segoe UI', sans-serif" font-size="12" fill="#34D399">&#10004; Debriefing CISO</text>
    <text x="14" y="138" font-family="'Segoe UI', sans-serif" font-size="12" fill="#34D399">&#10004; Mitigaci&#243;n en vivo</text>
  </g>
</svg>"""
    with open("assets/pfctl_decision_flow.svg", "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")
    print("Created assets/pfctl_decision_flow.svg")

def create_voice_soar_flow():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 750" width="100%" height="100%">
  <defs>
    <radialGradient id="bgGrad2" cx="50%" cy="50%" r="80%">
      <stop offset="0%" stop-color="#120A24" />
      <stop offset="60%" stop-color="#080414" />
      <stop offset="100%" stop-color="#03010A" />
    </radialGradient>

    <linearGradient id="headerPurple" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#8B5CF6" />
      <stop offset="100%" stop-color="#6D28D9" />
    </linearGradient>
    <linearGradient id="headerCyan" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00F5FF" />
      <stop offset="100%" stop-color="#0284C7" />
    </linearGradient>
    <linearGradient id="headerAmber" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#F59E0B" />
      <stop offset="100%" stop-color="#D97706" />
    </linearGradient>
    <linearGradient id="headerEmerald" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10B981" />
      <stop offset="100%" stop-color="#059669" />
    </linearGradient>

    <!-- Glows -->
    <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <filter id="glowPurple" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Grid -->
    <pattern id="grid2" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#2E1B4E" stroke-width="0.6" stroke-opacity="0.4" />
    </pattern>

    <!-- Markers -->
    <marker id="arrowCyan" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
      <polygon points="0 0, 8 3.5, 0 7" fill="#00F5FF" />
    </marker>
    <marker id="arrowPurple" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
      <polygon points="0 0, 8 3.5, 0 7" fill="#A855F7" />
    </marker>
    <marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
      <polygon points="0 0, 8 3.5, 0 7" fill="#F59E0B" />
    </marker>
    <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
      <polygon points="0 0, 8 3.5, 0 7" fill="#10B981" />
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1300" height="750" fill="url(#bgGrad2)" />
  <rect width="1300" height="750" fill="url(#grid2)" />

  <!-- Frame -->
  <rect x="20" y="20" width="1260" height="710" rx="12" fill="none" stroke="#2D1B4E" stroke-width="1.5" />
  <rect x="24" y="24" width="1252" height="702" rx="10" fill="none" stroke="#A855F7" stroke-width="0.7" stroke-opacity="0.3" stroke-dasharray="30 60" />

  <!-- ================= BANNER TITLE ================= -->
  <g transform="translate(650, 52)">
    <text x="0" y="0" font-family="'Orbitron', 'Segoe UI', sans-serif" font-size="24" font-weight="900" 
          letter-spacing="5" fill="#FFFFFF" text-anchor="middle">
      ARQUITECTURA SOAR : AGENTE DE VOZ IA &amp; TELEFON&#205;A ASTERISK
    </text>
    <text x="0" y="24" font-family="'Consolas', monospace" font-size="13" font-weight="bold" 
          letter-spacing="2" fill="#00F5FF" text-anchor="middle" filter="url(#glowCyan)">
      LLAMADA AUTOM&#193;TICA EN TIEMPO REAL &#8226; GOOGLE GEMINI LIVE FLASH 3.1 &#8226; DEBRIEFING AL CISO
    </text>
  </g>
  <line x1="60" y1="86" x2="1240" y2="86" stroke="#2D1B4E" stroke-width="2" />
  <line x1="380" y1="86" x2="920" y2="86" stroke="#A855F7" stroke-width="2.5" filter="url(#glowPurple)" />

  <!-- ================= STEP 1: INCIDENT WEBHOOK INGEST ================= -->
  <g transform="translate(60, 115)">
    <rect width="360" height="230" rx="10" fill="#170A26" stroke="#A855F7" stroke-width="2" filter="url(#glowPurple)" />
    <path d="M 0 10 Q 0 0 10 0 L 350 0 Q 360 0 360 10 L 360 38 L 0 38 Z" fill="url(#headerPurple)" />
    <text x="180" y="25" font-family="'Orbitron', sans-serif" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">1. DISPARO DE WEBHOOK (JSON)</text>

    <text x="16" y="66" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#D8B4FE">Emisor: Motor pfctl (Puerto 5000)</text>
    <text x="28" y="86" font-family="'Consolas', monospace" font-size="12" fill="#CBD5E1">POST http://127.0.0.1:5000/incident</text>

    <text x="16" y="114" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#38BDF8">Carga T&#225;ctica en Payload:</text>
    <text x="28" y="134" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#E2E8F0">&#8226; IP Atacante + País GeoIP MaxMind</text>
    <text x="28" y="154" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#E2E8F0">&#8226; Vector SQLi + Regla Suricata SID</text>
    <text x="28" y="174" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#E2E8F0">&#8226; Estado de Bloqueo en Tabla snort2c</text>

    <rect x="16" y="190" width="328" height="26" rx="4" fill="#2E124D" stroke="#A855F7" stroke-width="1" />
    <text x="180" y="208" font-family="'Consolas', monospace" font-size="11.5" font-weight="bold" fill="#E9D5FF" text-anchor="middle">&#9679; DESPACHO INMEDIATO: &lt; 50ms</text>
  </g>

  <!-- Arrow 1 -> 2 -->
  <path d="M 420 230 L 480 230" stroke="#A855F7" stroke-width="3.5" fill="none" marker-end="url(#arrowPurple)" filter="url(#glowPurple)" />

  <!-- ================= STEP 2: ASTERISK PBX & AMI DIALER ================= -->
  <g transform="translate(480, 115)">
    <rect width="360" height="230" rx="10" fill="#1C1405" stroke="#F59E0B" stroke-width="2" />
    <path d="M 0 10 Q 0 0 10 0 L 350 0 Q 360 0 360 10 L 360 38 L 0 38 Z" fill="url(#headerAmber)" />
    <text x="180" y="25" font-family="'Orbitron', sans-serif" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">2. ASTERISK PBX &amp; AUTO-DIAL</text>

    <text x="16" y="66" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#FBBF24">Asterisk Manager Interface (AMI):</text>
    <text x="28" y="86" font-family="'Consolas', monospace" font-size="12" fill="#FDE68A">Action: Originate</text>
    <text x="28" y="104" font-family="'Consolas', monospace" font-size="12" fill="#CBD5E1">Channel: PJSIP/1001 (CISO Mobile)</text>
    <text x="28" y="122" font-family="'Consolas', monospace" font-size="12" fill="#CBD5E1">Context: kronos-incident</text>
    <text x="28" y="140" font-family="'Consolas', monospace" font-size="12" fill="#CBD5E1">Exten: 1000 (Agente de Voz IA)</text>

    <rect x="16" y="165" width="328" height="50" rx="5" fill="#332005" stroke="#F59E0B" stroke-width="1.2" />
    <text x="180" y="184" font-family="'Consolas', monospace" font-size="11.5" font-weight="bold" fill="#FBBF24" text-anchor="middle">&#128222; REPIQUE TELEF&#211;NICO SIP INMEDIATO</text>
    <text x="180" y="202" font-family="'Segoe UI', sans-serif" font-size="11" fill="#FFFFFF" text-anchor="middle">Anexos: 1001 (Bruno), 1002, 1003, 1004</text>
  </g>

  <!-- Arrow 2 -> 3 -->
  <path d="M 840 230 L 900 230" stroke="#10B981" stroke-width="3.5" fill="none" marker-end="url(#arrowGreen)" />

  <!-- ================= STEP 3: CISO PICKUP ================= -->
  <g transform="translate(900, 115)">
    <rect width="340" height="230" rx="10" fill="#041A12" stroke="#10B981" stroke-width="2" />
    <path d="M 0 10 Q 0 0 10 0 L 330 0 Q 340 0 340 10 L 340 38 L 0 38 Z" fill="url(#headerEmerald)" />
    <text x="170" y="25" font-family="'Orbitron', sans-serif" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">3. ATENCI&#211;N DEL CISO</text>

    <text x="16" y="66" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#34D399">&#128241; Softphone / Canal VoIP Activo</text>
    <text x="28" y="86" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">CISO atiende la llamada en su dispositivo</text>

    <text x="16" y="114" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#34D399">&#128266; Apertura de Bridge de Audio</text>
    <text x="28" y="134" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">Audio PCM a 24kHz / 16-bit Mono</text>

    <rect x="16" y="165" width="308" height="50" rx="5" fill="#062E1D" stroke="#10B981" stroke-width="1.2" />
    <text x="170" y="184" font-family="'Consolas', monospace" font-size="11.5" font-weight="bold" fill="#6EE7B7" text-anchor="middle">&#10004; ENLACE ESTABLECIDO CON IA</text>
    <text x="170" y="202" font-family="'Segoe UI', sans-serif" font-size="11" fill="#FFFFFF" text-anchor="middle">Se inicia el di&#225;logo en directo</text>
  </g>

  <!-- Downwards Connectors to Step 4 & Step 5 -->
  <path d="M 650 345 L 650 415" stroke="#00F5FF" stroke-width="3.5" fill="none" marker-end="url(#arrowCyan)" filter="url(#glowCyan)" />

  <!-- ================= STEP 4: GEMINI LIVE FLASH 3.1 ENGINE ================= -->
  <g transform="translate(60, 420)">
    <rect width="680" height="265" rx="10" fill="#081A29" stroke="#00F5FF" stroke-width="2" filter="url(#glowCyan)" />
    <path d="M 0 10 Q 0 0 10 0 L 670 0 Q 680 0 680 10 L 680 40 L 0 40 Z" fill="url(#headerCyan)" />
    <text x="340" y="26" font-family="'Orbitron', sans-serif" font-size="15" font-weight="bold" fill="#000000" text-anchor="middle">4. GOOGLE GEMINI LIVE API FLASH 3.1 (VOICE BRIDGE)</text>

    <!-- 2 Sub-panels -->
    <g transform="translate(16, 55)">
      <text x="0" y="16" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#38BDF8">&#129302; Streaming Bidireccional WebSocket:</text>
      <text x="12" y="36" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">&#8226; Audio PCM full-duplex de ultrabaja latencia</text>
      <text x="12" y="56" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">&#8226; Capacidad de interrupci&#243;n (Barge-in)</text>
      <text x="12" y="76" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">&#8226; Comprensi&#243;n sem&#225;ntica y contexto t&#225;ctico</text>

      <text x="0" y="106" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#FBBF24">&#128227; Briefing Estructurado de Incidente:</text>
      <text x="12" y="126" font-family="'Consolas', monospace" font-size="12" fill="#FDE68A">"Alerta Cr&#237;tica: Se neutraliz&#243; un SQLi"</text>
      <text x="12" y="144" font-family="'Consolas', monospace" font-size="11.5" fill="#94A3B8">IP: 185.220.101.5 (Rusia) &#8226; Bloqueado</text>
    </g>

    <g transform="translate(360, 55)">
      <text x="0" y="16" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#34D399">&#128737; Asesor&#237;a y Mitigaciones en Vivo:</text>
      <text x="12" y="36" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">&#8226; Recomienda aislar subred DMZ</text>
      <text x="12" y="56" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">&#8226; Verifica si persisten otros vectores</text>
      <text x="12" y="76" font-family="'Segoe UI', sans-serif" font-size="12.5" fill="#CBD5E1">&#8226; Responde consultas t&#233;cnicas del CISO</text>

      <rect x="0" y="96" width="295" height="54" rx="5" fill="#031E2B" stroke="#00F5FF" stroke-width="1.2" />
      <text x="147" y="116" font-family="'Consolas', monospace" font-size="11" font-weight="bold" fill="#00F5FF" text-anchor="middle">LATENCIA DE VOZ: &lt; 800ms</text>
      <text x="147" y="136" font-family="'Segoe UI', sans-serif" font-size="11" fill="#FFFFFF" text-anchor="middle">Interlocuci&#243;n natural y fluida</text>
    </g>

    <!-- Bottom summary line -->
    <rect x="16" y="215" width="648" height="34" rx="4" fill="#051524" stroke="#1E293B" stroke-width="1" />
    <text x="340" y="236" font-family="'Consolas', monospace" font-size="11.5" font-weight="bold" fill="#38BDF8" text-anchor="middle">INTEGRACI&#211;N: gemini_live_client.py &#8596; gemini_audio_bridge.py (Audio RTP)</text>
  </g>

  <!-- Arrow Step 4 -> Step 5 -->
  <path d="M 740 550 L 800 550" stroke="#00F5FF" stroke-width="3.5" fill="none" marker-end="url(#arrowCyan)" filter="url(#glowCyan)" />

  <!-- ================= STEP 5: TACTICAL DECISION & HARDENING ================= -->
  <g transform="translate(800, 420)">
    <rect width="440" height="265" rx="10" fill="#1C0F2B" stroke="#A855F7" stroke-width="2" />
    <path d="M 0 10 Q 0 0 10 0 L 430 0 Q 440 0 440 10 L 440 40 L 0 40 Z" fill="url(#headerPurple)" />
    <text x="220" y="26" font-family="'Orbitron', sans-serif" font-size="15" font-weight="bold" fill="#FFFFFF" text-anchor="middle">5. RESPUESTA T&#193;CTICA DEL CISO</text>

    <text x="16" y="70" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="#E9D5FF">Comandos de Mitigaci&#243;n por Voz:</text>
    <text x="28" y="92" font-family="'Segoe UI', sans-serif" font-size="13" fill="#FFFFFF">&#8226; <tspan fill="#34D399" font-weight="bold">"Confirmar bloqueo permanente en pfBlockerNG"</tspan></text>
    <text x="28" y="114" font-family="'Segoe UI', sans-serif" font-size="13" fill="#FFFFFF">&#8226; <tspan fill="#38BDF8" font-weight="bold">"Aumentar sensibilidad de reglas en Suricata"</tspan></text>
    <text x="28" y="136" font-family="'Segoe UI', sans-serif" font-size="13" fill="#FFFFFF">&#8226; <tspan fill="#FBBF24" font-weight="bold">"Enviar reporte forense por email"</tspan></text>

    <!-- Success Outcome Box -->
    <rect x="16" y="158" width="408" height="85" rx="6" fill="#2E1045" stroke="#A855F7" stroke-width="1.5" />
    <text x="220" y="180" font-family="'Orbitron', sans-serif" font-size="13" font-weight="bold" fill="#34D399" text-anchor="middle">&#10004; INCIDENTE CONTENIDO EN &lt; 60 SEGUNDOS</text>
    <text x="220" y="204" font-family="'Segoe UI', sans-serif" font-size="12" fill="#E2E8F0" text-anchor="middle">Cero p&#233;rdida de datos &#8226; Cero tiempo muerto en DMZ</text>
    <text x="220" y="226" font-family="'Consolas', monospace" font-size="11" font-weight="bold" fill="#00F5FF" text-anchor="middle">TELEMETR&#205;A COMPLETA REGISTRADA EN SIEM / LOGS</text>
  </g>
</svg>"""
    with open("assets/voice_soar_flow.svg", "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")
    print("Created assets/voice_soar_flow.svg")

if __name__ == "__main__":
    create_pfctl_decision_flow()
    create_voice_soar_flow()
