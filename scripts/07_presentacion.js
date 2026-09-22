// 5-slide deck: ELPI overview / verbatim questions (child, caregiver) /
// sampling & attrition / Gillmore specification (Beamer image).
// Deps: npm i pptxgenjs react-icons react react-dom sharp
// Slide 5 embeds spec-1.png, rendered from 07_gillmore_spec.tex:
//   pdflatex 07_gillmore_spec.tex && pdftoppm -png -r 640 07_gillmore_spec.pdf spec
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

// ---------- palette (matches repo figures) ----------
const INK = "0B0B0B";
const MUT = "52514E";
const FAINT = "898781";
const NAVY = "1E3D5C";
const BLUE = "2A78D6";
const ORANGE = "EB6834";
const TINT = "EDF3FC";   // light blue card
const CARD = "F4F4F0";   // light neutral card
const GRAY = "C9C8BF";   // refresh bar
const GRAY2 = "E0DFD7";  // refresh bar (new sample)
const SER = "Cambria";   // headers + equation
const SANS = "Arial";    // body

async function iconPng(Comp) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Comp, { size: 256, color: "#FFFFFF" })
  );
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pptx.author = "ELPI project";
  pptx.title = "ELPI and the 27-F design";

  // =====================================================================
  // SLIDE 1 — What ELPI is + variable map
  // =====================================================================
  const s1 = pptx.addSlide();
  s1.background = { color: "FFFFFF" };

  s1.addText("The ELPI: Chile’s national child cohort", {
    x: 0.5, y: 0.26, w: 12.33, h: 0.54, fontFace: SER, fontSize: 30, bold: true,
    color: INK, align: "left", margin: 0, isTextBox: true,
  });
  s1.addText(
    "Encuesta Longitudinal de Primera Infancia — a birth-cohort panel following the same children from infancy to adolescence: caregiver interviews plus standardized child assessments administered in the home. Public microdata and codebooks (Ministry of Social Development).",
    { x: 0.5, y: 0.88, w: 12.33, h: 0.52, fontFace: SANS, fontSize: 12, color: MUT,
      align: "left", margin: 0, isTextBox: true }
  );

  // ---- stat band
  const stats = [
    ["15,175", "children enrolled in 2010; representative of the 2006–09 birth cohorts"],
    ["4 waves", "2010 · 2012 · 2017 · 2024, plus refresh samples in 2012 and 2017"],
    ["0–4 → 14–18", "ages covered — the same children from cradle to adolescence"],
    ["folio", "child-level ID links every wave; comuna strata & longitudinal weights"],
  ];
  const SBX = 0.5, SBY = 1.56, SBW = 2.865, SBH = 0.98, SBG = 0.29;
  stats.forEach((st, k) => {
    const x = SBX + k * (SBW + SBG);
    s1.addShape(pptx.ShapeType.roundRect, {
      x, y: SBY, w: SBW, h: SBH, fill: { color: TINT }, line: { type: "none" },
      rectRadius: 0.06,
    });
    s1.addText(st[0], {
      x: x + 0.14, y: SBY + 0.05, w: SBW - 0.28, h: 0.4, fontFace: SER,
      fontSize: 21, bold: true, color: NAVY, italic: st[0] === "folio",
      align: "left", margin: 0, isTextBox: true,
    });
    s1.addText(st[1], {
      x: x + 0.14, y: SBY + 0.44, w: SBW - 0.28, h: 0.5, fontFace: SANS,
      fontSize: 8.6, color: MUT, align: "left", margin: 0, isTextBox: true,
    });
  });

  // ---- domain grid
  s1.addText("WHAT IT MEASURES — EVERY DOMAIN OF THE CHILD’S LIFE", {
    x: 0.5, y: 2.7, w: 12.33, h: 0.26, fontFace: SANS, fontSize: 10.5, bold: true,
    color: FAINT, charSpacing: 2, align: "left", margin: 0, isTextBox: true,
  });

  const icons = {
    brain: await iconPng(fa.FaBrain),
    smile: await iconPng(fa.FaSmile),
    heart: await iconPng(fa.FaHeartbeat),
    child: await iconPng(fa.FaChild),
    grad: await iconPng(fa.FaGraduationCap),
    home: await iconPng(fa.FaHome),
    hands: await iconPng(fa.FaHandsHelping),
    brief: await iconPng(fa.FaBriefcase),
    warn: await iconPng(fa.FaExclamationTriangle),
  };

  const cards = [
    ["brain", "Cognitive skills",
     "TVIP/Peabody vocabulary in all 4 waves · EEDP & TADI infant development · Battelle screening · Woodcock-Muñoz · digit span & Hearts-and-Flowers (executive function)"],
    ["smile", "Non-cognitive skills",
     "CBCL socio-emotional problem-behavior scales in every wave (internalizing & externalizing syndromes) · ASQ:SE screening (2010–17)"],
    ["heart", "Mental health & risk (14–18)",
     "PHQ-2 depression & GAD-2 anxiety screens · 10-item ACEs battery · smoking, alcohol & drug use · self-reported GPA (2024)"],
    ["child", "Health & growth",
     "Birth weight & gestational age · measured height/weight with WHO z-scores (2010–17) · maternal smoking in pregnancy · breastfeeding"],
    ["grad", "Education & childcare",
     "Childcare & preschool histories from birth · enrollment, grade & school type in every wave · maternal schooling"],
    ["home", "Family structure",
     "Full household roster each wave · marriage, divorce & separation — incl. child’s age when a parent left the home · father presence"],
    ["hands", "Parenting & home environment",
     "HOME inventory (observed 2012 / reported 2017) · discipline & parenting practices · parental involvement & self-efficacy"],
    ["brief", "Caregiver & household",
     "Maternal depression (EPDS, CES-D) & parental stress (PSI) · work histories by child’s age · income · Chile Crece Contigo · 27-F earthquake module (2012)"],
  ];
  const GX = 0.5, GY = 3.02, CW = 2.865, CH = 1.92, GGX = 0.29, GGY = 0.24;
  cards.forEach((c, k) => {
    const x = GX + (k % 4) * (CW + GGX);
    const y = GY + Math.floor(k / 4) * (CH + GGY);
    s1.addShape(pptx.ShapeType.roundRect, {
      x, y, w: CW, h: CH, fill: { color: "FFFFFF" }, line: { color: "E1E0D9", width: 1 },
      rectRadius: 0.06, shadow: { type: "outer", color: "D9D8D2", blur: 6, offset: 1, angle: 90, opacity: 0.35 },
    });
    s1.addShape(pptx.ShapeType.ellipse, {
      x: x + 0.14, y: y + 0.13, w: 0.4, h: 0.4, fill: { color: BLUE }, line: { type: "none" },
    });
    s1.addImage({ data: icons[c[0]], x: x + 0.235, y: y + 0.225, w: 0.21, h: 0.21 });
    s1.addText(c[1], {
      x: x + 0.64, y: y + 0.13, w: CW - 0.76, h: 0.42, fontFace: SANS, fontSize: 11.6,
      bold: true, color: NAVY, align: "left", valign: "middle", margin: 0, isTextBox: true,
    });
    s1.addText(c[2], {
      x: x + 0.16, y: y + 0.62, w: CW - 0.32, h: CH - 0.76, fontFace: SANS, fontSize: 9.2,
      color: MUT, align: "left", valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.06,
    });
  });

  s1.addText(
    "Source: ELPI public microdata & codebooks, waves 2010–2024 — observatorio.ministeriodesarrollosocial.gob.cl (instrument coverage by wave in parentheses).",
    { x: 0.5, y: 7.14, w: 12.33, h: 0.24, fontFace: SANS, fontSize: 8, color: FAINT,
      align: "left", margin: 0, isTextBox: true }
  );
  s1.addNotes("ELPI overview: survey design facts on top; eight variable domains with instruments and wave coverage. All coverage claims verified against the microdata and codebooks in the TALIS repo.");

  // =====================================================================
  // SLIDE 2 — Verbatim questions: the child & adolescent
  // =====================================================================
  const label = (s, y, txt) => s.addText(txt, {
    x: 0.5, y, w: 12.33, h: 0.26, fontFace: SANS, fontSize: 10.5, bold: true,
    color: FAINT, charSpacing: 2, align: "left", margin: 0, isTextBox: true,
  });
  const quote = (s, x, y, w, q, tag, qSize, lines) => {
    s.addText("“" + q + "”", {
      x, y, w, h: 0.4, fontFace: SER, fontSize: qSize || 10.5, italic: true,
      color: INK, align: "left", valign: "top", margin: 0, isTextBox: true,
      lineSpacingMultiple: 1.02,
    });
    s.addText(tag, {
      x, y: y + ((lines || 2) === 2 ? 0.42 : 0.24), w, h: 0.16, fontFace: SANS, fontSize: 7.8, color: FAINT,
      align: "left", margin: 0, isTextBox: true,
    });
  };

  const q1 = pptx.addSlide();
  q1.background = { color: "FFFFFF" };
  q1.addText("What we ask the child — verbatim", {
    x: 0.5, y: 0.26, w: 12.33, h: 0.54, fontFace: SER, fontSize: 30, bold: true,
    color: INK, align: "left", margin: 0, isTextBox: true,
  });
  q1.addText(
    "Standardized tests administered by a trained evaluator — and, from 2024, a sensitive module the adolescent answers alone. Quotes are verbatim from the official microdata (variable labels), sic.",
    { x: 0.5, y: 0.88, w: 12.33, h: 0.34, fontFace: SANS, fontSize: 12, color: MUT,
      align: "left", margin: 0, isTextBox: true }
  );

  label(q1, 1.34, "THE EVALUATOR, WITH THE CHILD");
  const tests = [
    ["TVIP · all four waves",
     "The child hears a word and points to 1 of 4 pictures — receptive vocabulary (Peabody, Hispanic norms)."],
    ["“Juego del Corazón / de la Flor” · 2017",
     "Hearts & Flowers: computerized inhibition task — % correct and reaction times (executive function)."],
    ["Backward digit span · 2012–17",
     "The child repeats digit strings in reverse order — working memory."],
  ];
  tests.forEach((t, k) => {
    const x = 0.5 + k * (4.05 + 0.09);
    q1.addShape(pptx.ShapeType.roundRect, {
      x, y: 1.62, w: 4.05, h: 0.86, fill: { color: TINT }, line: { type: "none" }, rectRadius: 0.06,
    });
    q1.addText(t[0], {
      x: x + 0.14, y: 1.7, w: 3.77, h: 0.22, fontFace: SANS, fontSize: 10.3, bold: true,
      color: NAVY, align: "left", margin: 0, isTextBox: true,
    });
    q1.addText(t[1], {
      x: x + 0.14, y: 1.94, w: 3.77, h: 0.48, fontFace: SANS, fontSize: 8.8, color: MUT,
      align: "left", margin: 0, isTextBox: true, lineSpacingMultiple: 1.04,
    });
  });

  label(q1, 2.66, "THE ADOLESCENT ANSWERS ALONE — SELF-COMPLETED MODULE, 2024 (AGES 14–18)");
  const adol = [
    ["¿Te has sentido bajoneado(a), deprimido(a), irritable o desesperanzado(a)?",
     "d4_1 · PHQ-2, depression screen"],
    ["¿Te has sentido muy nervioso(a), angustiado(a) o con los nervios de punta?",
     "d4_3 · GAD-2, anxiety screen"],
    ["Ha presenciado peleas o amenazas entre los integrantes del hogar",
     "aces_2 · adverse childhood experiences (ACEs)"],
    ["Vivió o vive con personas que tenían un problema de consumo excesivo de alcohol, drogas o medicinas",
     "aces_10 · adverse childhood experiences (ACEs)"],
    ["¿Has fumado cigarrillos de tabaco alguna vez en los últimos 12 meses?",
     "g11 · tobacco use"],
    ["¿Cuántos días consumiste alcohol la semana pasada?",
     "g12_frec · alcohol use"],
    ["¿En los últimos 12 meses has recibido llamadas al celular insultantes o amenazantes?",
     "g2_3 · cyberbullying / victimization"],
    ["¿Qué promedio de notas tuviste el año pasado?",
     "e3_asiste · self-reported GPA (Chilean 1–7 scale)"],
  ];
  adol.forEach((e, k) => {
    const x = k % 2 === 0 ? 0.5 : 6.88;
    const y = 2.98 + Math.floor(k / 2) * 0.74;
    quote(q1, x, y, 5.95, e[0], e[1]);
  });

  label(q1, 6.02, "AND ALREADY AT AGES 8–12 — THE CHILD SELF-REPORTS (2017)");
  quote(q1, 0.5, 6.3, 5.95,
    "¿Piensas que en tu colegio hay estudiantes que fuman cigarrillos…?",
    "d13 · child questionnaire, risk environment at school");
  quote(q1, 6.88, 6.3, 5.95,
    "En la última semana, ¿tú y alguien de tu familia leyeron juntos libros…?",
    "b17 · child questionnaire, family reading");

  q1.addText(
    "Verbatim variable labels from the ELPI public microdata; 2010–12 files store labels truncated at 80 characters (ellipses). Bracketed terms replace questionnaire placeholders.",
    { x: 0.5, y: 7.14, w: 12.33, h: 0.24, fontFace: SANS, fontSize: 8, color: FAINT,
      align: "left", margin: 0, isTextBox: true }
  );
  q1.addNotes("Verbatim questions, child side: evaluator-administered tests (TVIP, Hearts & Flowers, digit span), the 2024 self-completed adolescent module (PHQ-2 d4_1, GAD-2 d4_3, ACEs aces_2/aces_10, tobacco g11, alcohol g12_frec, cyberbullying g2_3, GPA e3_asiste), and 2017 child self-reports (d13, b17).");

  // =====================================================================
  // SLIDE 3 — Verbatim questions: the caregiver & household
  // =====================================================================
  const q2 = pptx.addSlide();
  q2.background = { color: "FFFFFF" };
  q2.addText("What we ask the caregiver — verbatim", {
    x: 0.5, y: 0.26, w: 12.33, h: 0.54, fontFace: SER, fontSize: 30, bold: true,
    color: INK, align: "left", margin: 0, isTextBox: true,
  });
  q2.addText(
    "The main caregiver (usually the mother) is interviewed at home in every wave — retrospective pregnancy modules, screened mental-health scales, observed parenting, income, programs, and a dedicated 27-F module in 2012.",
    { x: 0.5, y: 0.88, w: 12.33, h: 0.34, fontFace: SANS, fontSize: 12, color: MUT,
      align: "left", margin: 0, isTextBox: true }
  );

  const group = (s, x, y, iconKey, title) => {
    s.addShape(pptx.ShapeType.ellipse, {
      x, y, w: 0.3, h: 0.3, fill: { color: BLUE }, line: { type: "none" },
    });
    s.addImage({ data: icons[iconKey], x: x + 0.075, y: y + 0.075, w: 0.15, h: 0.15 });
    s.addText(title, {
      x: x + 0.42, y, w: 5.5, h: 0.3, fontFace: SANS, fontSize: 11.5, bold: true,
      color: NAVY, align: "left", valign: "middle", margin: 0, isTextBox: true,
    });
  };
  const HDR = 0.36, GAP = 0.12;
  const col = (s, x, groups) => {
    let y = 1.42;
    groups.forEach(g => {
      group(s, x, y, g.icon, g.title);
      y += HDR;
      g.items.forEach(it => {
        quote(s, x + 0.02, y, 5.85, it[0], it[1], 10, it[2]);
        y += it[2] === 2 ? 0.62 : 0.44;
      });
      y += GAP;
    });
  };
  col(q2, 0.5, [
    { icon: "home", title: "Family structure & separation", items: [
      ["\u00bfQu\u00e9 edad ten\u00eda [el/la adolescente] cuando la madre dej\u00f3 de vivir con \u00e9l(ella)?",
       "m1 \u00b7 2024 (also 2017; asked for mother and father) \u00b7 separation timing", 2],
    ]},
    { icon: "child", title: "Pregnancy & birth (retrospective)", items: [
      ["Durante el embarazo del(de la) ni\u00f1o(a) seleccionado(a), \u00bffum\u00f3 cigarrillos?",
       "b8 \u00b7 2012 (also 2010 g7a) \u00b7 smoking in pregnancy", 1],
      ["\u00bfEl embarazo del(de la) ni\u00f1o(a) seleccionado(a) fue planificado?",
       "b36 \u00b7 2012 \u00b7 planned pregnancy", 1],
    ]},
    { icon: "heart", title: "Caregiver mental health (screened scales)", items: [
      ["Me sent\u00ed deprimido/a \u2014 Sent\u00ed que todo lo que hac\u00eda me costaba un gran esfuerzo",
       "cesd_p1d / cesd_p1e \u00b7 CES-D-10 depression, 2017 & 2024", 2],
      ["Ser cuidador/a me pone tenso/a y ansioso/a",
       "pscs_p16 \u00b7 parental self-efficacy scale (PSCS), 2017 & 2024", 1],
      ["EPDS postpartum depression score \u2014 incl. a \u2018Pensamientos Suicidas\u2019 flag",
       "epds_pb / epds_ps \u00b7 2012 \u00b7 plus Parental Stress Index (PSI) 2012\u20132024", 1],
    ]},
    { icon: "brief", title: "Household economy", items: [
      ["En [mes pasado], \u00bfcu\u00e1l fue el ingreso de [nombre] proveniente de su o sus trabajos, ocupaci\u00f3n o actividad?",
       "y1 \u00b7 2024 \u00b7 income module y1\u2013y5, per household member", 2],
    ]},
  ]);
  col(q2, 6.88, [
    { icon: "hands", title: "Parenting \u2014 reported and observed", items: [
      ["Le dio una palmada o cachetada en alguna parte del cuerpo",
       "pc4_6 \u00b7 2024 \u00b7 discipline in the last month (also 2012 f20c\u2013g)", 1],
      ["\u00bfCree usted que para criar o educar correctamente a un adolescente, se le debe castigar f\u00edsicamente?",
       "pc5 \u00b7 2024 \u00b7 attitudes toward corporal punishment", 2],
      ["La Madre o tutora lee historias al(a la) ni\u00f1o(a), al menos tres veces a la\u2026",
       "h11 \u00b7 2010 \u00b7 HOME inventory \u2014 marked by the evaluator observing the home", 1],
    ]},
    { icon: "warn", title: "The 27-F earthquake module (2012)", items: [
      ["Producto del terremoto/tsunami, \u00bfla vivienda que habitaba el(la) ni\u00f1o(a)\u2026?",
       "h3 \u00b7 housing damage", 1],
      ["Recuerdos traum\u00e1ticos del terremoto \u2014 stress/angustia/ansiedad \u2014 miedo/p\u00e1nico",
       "h4_2\u2013h4_5 \u00b7 post-quake symptom checklist", 2],
      ["\u00bfUsted consult\u00f3 a un psic\u00f3logo o psiquiatra a causa de estos s\u00edntomas?",
       "h5 \u00b7 mental-health care take-up after 27-F", 1],
    ]},
    { icon: "grad", title: "Programs & the home", items: [
      ["\u00bfConoce o ha escuchado hablar del programa Chile Crece Contigo?",
       "f27 \u00b7 2012 \u00b7 program awareness & receipt (f29: materials received)", 1],
      ["\u00bfM\u00e1s o menos cu\u00e1ntos libros infantiles o juveniles tiene en su casa?",
       "home1 \u00b7 2024 \u00b7 HOME, books at home", 1],
    ]},
  ]);

  q2.addText(
    "Verbatim variable labels from the ELPI public microdata; 2010–12 files store labels truncated at 80 characters (ellipses). Bracketed terms replace questionnaire placeholders (%nombre%, %mes pasado%).",
    { x: 0.5, y: 7.14, w: 12.33, h: 0.24, fontFace: SANS, fontSize: 8, color: FAINT,
      align: "left", margin: 0, isTextBox: true }
  );
  q2.addNotes("Verbatim questions, caregiver side: separation timing (m1/p1), pregnancy retrospectives (b8, b36), mental-health scales (CES-D, PSCS, EPDS incl. suicidal-thoughts flag, PSI), discipline reported (pc4, pc5) and HOME observed (h11), the 2012 earthquake module (h3, h4, h5), income (y1) and Chile Crece Contigo (f27/f29).");

  // =====================================================================
  // SLIDE 2 — Sampling evolution / attrition
  // =====================================================================
  const s2 = pptx.addSlide();
  s2.background = { color: "FFFFFF" };

  s2.addText("Four waves, one generation: sampling & attrition", {
    x: 0.5, y: 0.26, w: 12.33, h: 0.54, fontFace: SER, fontSize: 30, bold: true,
    color: INK, align: "left", margin: 0, isTextBox: true,
  });
  s2.addText(
    "The original 2010 cohort is re-interviewed in every wave; refresh samples added in 2012 and 2017 were not re-fielded in 2024.",
    { x: 0.5, y: 0.88, w: 12.33, h: 0.32, fontFace: SANS, fontSize: 12.5, color: MUT,
      align: "left", margin: 0, isTextBox: true }
  );

  // bar geometry
  const YB = 5.42;               // baseline
  const S = 3.32 / 17307;        // inches per child
  const BW = 1.4;
  const LEFTS = [0.9, 3.15, 5.4, 7.65];
  const blue = [15175, 12898, 10230, 10003];
  const bh = blue.map(n => n * S);

  // blue original-cohort bars
  LEFTS.forEach((x, k) => {
    s2.addShape(pptx.ShapeType.rect, {
      x, y: YB - bh[k], w: BW, h: bh[k], fill: { color: BLUE }, line: { type: "none" },
    });
    s2.addText(blue[k].toLocaleString("en-US"), {
      x, y: YB - bh[k] + 0.06, w: BW, h: 0.3, fontFace: SANS, fontSize: 13.5, bold: true,
      color: "FFFFFF", align: "center", margin: 0, isTextBox: true,
    });
  });

  // refresh stacks: 2012 +3,135 ; 2017 +2,142 and +4,935
  const seg = (x, yTop, h, color, label, txtColor) => {
    s2.addShape(pptx.ShapeType.rect, {
      x, y: yTop, w: BW, h, fill: { color }, line: { color: "FFFFFF", width: 0.75 },
    });
    if (label) s2.addText(label, {
      x, y: yTop + h / 2 - 0.11, w: BW, h: 0.22, fontFace: SANS, fontSize: 8.3,
      color: txtColor, align: "center", margin: 0, isTextBox: true,
    });
  };
  // 2012
  const r12h = 3135 * S;
  seg(LEFTS[1], YB - bh[1] - r12h, r12h, GRAY, "+3,135", INK);
  // 2017
  const r17a = 2142 * S, r17b = 4935 * S;
  seg(LEFTS[2], YB - bh[2] - r17a, r17a, GRAY, "+2,142", INK);
  seg(LEFTS[2], YB - bh[2] - r17a - r17b, r17b, GRAY2, "+4,935", MUT);

  // totals above the two stacked waves
  s2.addText("16,033 interviewed", {
    x: LEFTS[1] - 0.4, y: YB - bh[1] - r12h - 0.26, w: BW + 0.8, h: 0.22,
    fontFace: SANS, fontSize: 9, color: FAINT, align: "center", margin: 0, isTextBox: true,
  });
  s2.addText("17,307 interviewed", {
    x: LEFTS[2] - 0.4, y: YB - bh[2] - r17a - r17b - 0.26, w: BW + 0.8, h: 0.22,
    fontFace: SANS, fontSize: 9, color: FAINT, align: "center", margin: 0, isTextBox: true,
  });

  // retention arrows between blue bars
  const rets = ["85.0%", "79.3%", "97.8%"];
  rets.forEach((r, k) => {
    const gapC = (LEFTS[k] + BW + LEFTS[k + 1]) / 2;
    s2.addText(r, {
      x: gapC - 0.55, y: 3.98, w: 1.1, h: 0.26, fontFace: SANS, fontSize: 13.5, bold: true,
      color: NAVY, align: "center", margin: 0, isTextBox: true,
    });
    s2.addShape(pptx.ShapeType.rightArrow, {
      x: gapC - 0.34, y: 4.3, w: 0.68, h: 0.24, fill: { color: NAVY }, line: { type: "none" },
    });
    s2.addText("retained", {
      x: gapC - 0.55, y: 4.6, w: 1.1, h: 0.2, fontFace: SANS, fontSize: 8.2,
      color: FAINT, align: "center", margin: 0, isTextBox: true,
    });
  });

  // x-axis labels
  const years = ["2010", "2012", "2017–18", "2024"];
  const waves = ["Wave 1", "Wave 2", "Wave 3", "Wave 4"];
  const ages = ["ages 0–4", "ages 2–6", "ages 8–12", "ages 14–18"];
  const stages = ["Infancy", "Early childhood", "Middle childhood", "Adolescence"];
  LEFTS.forEach((x, k) => {
    const bx = x - 0.4, bw2 = BW + 0.8;
    s2.addText(years[k], {
      x: bx, y: YB + 0.1, w: bw2, h: 0.3, fontFace: SER, fontSize: 16, bold: true,
      color: NAVY, align: "center", margin: 0, isTextBox: true,
    });
    s2.addText(waves[k] + " · " + ages[k], {
      x: bx, y: YB + 0.42, w: bw2, h: 0.22, fontFace: SANS, fontSize: 9.5,
      color: INK, align: "center", margin: 0, isTextBox: true,
    });
    s2.addText(stages[k], {
      x: bx, y: YB + 0.65, w: bw2, h: 0.22, fontFace: SANS, fontSize: 9.5, italic: true,
      color: FAINT, align: "center", margin: 0, isTextBox: true,
    });
  });

  // legend
  s2.addShape(pptx.ShapeType.rect, { x: 0.9, y: 6.62, w: 0.18, h: 0.18, fill: { color: BLUE }, line: { type: "none" } });
  s2.addText("Original 2010 cohort — followed in every wave", {
    x: 1.14, y: 6.6, w: 3.6, h: 0.22, fontFace: SANS, fontSize: 9.5, color: INK,
    align: "left", margin: 0, isTextBox: true,
  });
  s2.addShape(pptx.ShapeType.rect, { x: 4.85, y: 6.62, w: 0.18, h: 0.18, fill: { color: GRAY }, line: { type: "none" } });
  s2.addText("Refresh samples — 2012: +3,135 born 2010–11; 2017: +2,142 of them re-interviewed and +4,935 born 2015–17; none re-fielded in 2024", {
    x: 5.09, y: 6.6, w: 7.7, h: 0.36, fontFace: SANS, fontSize: 9.5, color: INK,
    align: "left", margin: 0, isTextBox: true,
  });

  // right panel callouts
  const RX = 9.85, RW = 3.0;
  s2.addText("34.1%", {
    x: RX, y: 1.72, w: RW, h: 0.72, fontFace: SER, fontSize: 44, bold: true,
    color: ORANGE, align: "left", margin: 0, isTextBox: true,
  });
  s2.addText("cumulative attrition of the original cohort over 14 years — 65.9% of the 2010 infants are still in the panel as adolescents", {
    x: RX, y: 2.46, w: RW, h: 0.72, fontFace: SANS, fontSize: 10.5, color: MUT,
    align: "left", margin: 0, isTextBox: true,
  });
  s2.addText("10,003", {
    x: RX, y: 3.34, w: RW, h: 0.52, fontFace: SER, fontSize: 30, bold: true,
    color: NAVY, align: "left", margin: 0, isTextBox: true,
  });
  s2.addText("adolescents aged 14–18 in 2024 — every one of them enrolled as an infant in 2010", {
    x: RX, y: 3.88, w: RW, h: 0.52, fontFace: SANS, fontSize: 10.5, color: MUT,
    align: "left", margin: 0, isTextBox: true,
  });
  s2.addShape(pptx.ShapeType.roundRect, {
    x: RX, y: 4.62, w: RW, h: 1.14, fill: { color: TINT }, line: { type: "none" }, rectRadius: 0.06,
  });
  s2.addText([
    { text: "Clean 14-year panel: ", options: { bold: true, color: NAVY } },
    { text: "wave 4 re-fielded only the original cohort. Balanced panel present in all four waves: ", options: { color: MUT } },
    { text: "7,012 children.", options: { bold: true, color: NAVY } },
  ], {
    x: RX + 0.15, y: 4.74, w: RW - 0.3, h: 0.9, fontFace: SANS, fontSize: 10.5,
    align: "left", margin: 0, isTextBox: true,
  });

  s2.addText(
    "Counts: children interviewed per wave, by sample of origin (own tabulations from ELPI microdata via the child ID; wave-3 evaluation sample: 15,827). Attrition figure consistent with the ELPI cohort profile.",
    { x: 0.5, y: 7.14, w: 12.33, h: 0.24, fontFace: SANS, fontSize: 8, color: FAINT,
      align: "left", margin: 0, isTextBox: true }
  );
  s2.addNotes("Bars to scale. Blue = original 2010 cohort (15,175 -> 12,898 -> 10,230 -> 10,003; 85.0% / 79.3% / 97.8% between-wave retention; 34.1% cumulative attrition). Gray = refresh samples (2012: +3,135; 2017: +2,142 re-interviewed + 4,935 new), not followed in 2024.");

  // =====================================================================
  // SLIDE 5 — Gillmore specification (Beamer/LaTeX render, full-bleed)
  // =====================================================================
  const s3 = pptx.addSlide();
  s3.background = { color: "FFFFFF" };
  s3.addImage({ path: "spec-1.png", x: 0, y: 0, w: 13.333, h: 7.5 });
  s3.addNotes("Specification slide typeset in LaTeX (Beamer, Computer Modern) and embedded as a full-bleed image; source gillmore_spec.tex in the repo. Eq. (2.1) verbatim from the dissertation chapter; identification incl. lower-bound argument; validity checks.");


  // =====================================================================
  // SLIDE 6 — Diagrama: el DiD de Gillmore (cohortes x olas x edades)
  // =====================================================================
  const GREEN = "1BAF7A";
  const s6 = pptx.addSlide();
  s6.background = { color: "FFFFFF" };
  s6.addText("El DiD de Gillmore: cohortes, olas y edades", {
    x: 0.5, y: 0.26, w: 12.33, h: 0.54, fontFace: SER, fontSize: 30, bold: true,
    color: INK, align: "left", margin: 0, isTextBox: true,
  });
  s6.addText(
    "Affected = 1 si el niño tenía 0–4 años (o estaba en gestación) el 27-F. El grupo de control —concebidos después— solo existe gracias a los refrescos… y no fue re-entrevistado en 2024.",
    { x: 0.5, y: 0.86, w: 12.33, h: 0.32, fontFace: SANS, fontSize: 11.5,
      color: MUT, align: "left", margin: 0, isTextBox: true });

  const xm = (yr) => 2.9 + (yr - 2006) * 0.5155;
  const C12 = xm(2012.4), C17 = xm(2017.4), C24 = xm(2024.3);

  // bandas de ola
  [[C12, "OLA 2012"], [C17, "OLA 2017"], [C24, "OLA 2024"]].forEach(([cx, t]) => {
    s6.addShape(pptx.ShapeType.roundRect, {
      x: cx - 0.33, y: 1.58, w: 0.66, h: 3.34, fill: { color: TINT },
      line: { type: "none" }, rectRadius: 0.05,
    });
    s6.addText(t, { x: cx - 0.7, y: 1.32, w: 1.4, h: 0.22, fontFace: SANS,
      fontSize: 9.5, bold: true, color: NAVY, align: "center", margin: 0,
      isTextBox: true });
  });
  // linea 27-F
  const X27 = xm(2010.15);
  s6.addShape(pptx.ShapeType.rect, { x: X27 - 0.015, y: 1.5, w: 0.03, h: 3.5,
    fill: { color: "C0392B" }, line: { type: "none" } });
  s6.addText("27-F (8,8 Mw)", { x: X27 - 0.8, y: 1.1, w: 1.6, h: 0.2,
    fontFace: SANS, fontSize: 9.5, bold: true, color: "C0392B",
    align: "center", margin: 0, isTextBox: true });

  // filas
  const rowbar = (y, x0, fill, line) => s6.addShape(pptx.ShapeType.roundRect, {
    x: x0, y: y - 0.15, w: 12.75 - x0, h: 0.3, fill: { color: fill },
    line: { color: line, width: 1 }, rectRadius: 0.08,
  });
  const dot = (cx, y, color) => s6.addShape(pptx.ShapeType.ellipse, {
    x: cx - 0.14, y: y - 0.14, w: 0.28, h: 0.28, fill: { color },
    line: { color: "FFFFFF", width: 1.5 },
  });
  const age = (cx, y, t, color) => s6.addText(t, {
    x: cx - 0.55, y: y - 0.47, w: 1.1, h: 0.2, fontFace: SANS, fontSize: 10,
    bold: true, color, align: "center", margin: 0, isTextBox: true });
  const rol = (cx, y, t) => s6.addText(t, {
    x: cx - 0.6, y: y + 0.2, w: 1.2, h: 0.18, fontFace: SANS, fontSize: 8,
    color: FAINT, align: "center", margin: 0, isTextBox: true });
  const lab = (y, l1, l2) => {
    s6.addText(l1, { x: 0.5, y: y - 0.3, w: 2.3, h: 0.2, fontFace: SANS,
      fontSize: 9.5, bold: true, color: INK, align: "left", margin: 0,
      isTextBox: true });
    s6.addText(l2, { x: 0.5, y: y - 0.09, w: 2.3, h: 0.42, fontFace: SANS,
      fontSize: 8, color: MUT, align: "left", margin: 0, isTextBox: true });
  };

  const RWA = 2.15, RWB = 3.35, RWC = 4.25;
  // fila A: tratados
  rowbar(RWA, xm(2006), "CFE0F6", BLUE);
  lab(RWA, "AFFECTED = 1", "Nacidos 2006–nov 2010: 0–4 años el 27-F (los de mar–nov 2010 entran vía refresco 2012)");
  dot(C12, RWA, BLUE);  age(C12, RWA, "2–6", NAVY);  rol(C12, RWA, "corto plazo");
  dot(C17, RWA, BLUE);  age(C17, RWA, "7–11", NAVY); rol(C17, RWA, "mediano");
  dot(C24, RWA, NAVY);  age(C24, RWA, "14–18", NAVY); rol(C24, RWA, "largo (2024)");
  // fila B: control refresco 2012
  rowbar(RWB, xm(2011), "D2EBDD", GREEN);
  lab(RWB, "AFFECTED = 0", "Nacidos 2011 — refresco 2012");
  dot(C17, RWB, GREEN); age(C17, RWB, "5–6", "0E7A54"); rol(C17, RWB, "control");
  // fila C: control refresco 2017
  rowbar(RWC, xm(2012), "D2EBDD", GREEN);
  lab(RWC, "AFFECTED = 0", "Nacidos 2012–2015 — refresco 2017");
  dot(C17, RWC, GREEN); age(C17, RWC, "2–5", "0E7A54"); rol(C17, RWC, "control");
  // cruces 2024
  [[RWB], [RWC]].forEach(([y]) => s6.addText("✕", {
    x: C24 - 0.2, y: y - 0.19, w: 0.4, h: 0.36, fontFace: SANS, fontSize: 16,
    bold: true, color: "C0392B", align: "center", margin: 0, isTextBox: true }));
  s6.addText("no re-entrevistados", { x: C24 - 0.85, y: RWC + 0.28, w: 1.7,
    h: 0.2, fontFace: SANS, fontSize: 8, bold: true, color: "C0392B",
    align: "center", margin: 0, isTextBox: true });

  // marcadores "entra a la ELPI" (anillo blanco con borde) + regla de lectura
  const entra = (cx, y, t) => {
    s6.addShape(pptx.ShapeType.ellipse, { x: cx - 0.09, y: y - 0.09,
      w: 0.18, h: 0.18, fill: { color: "FFFFFF" },
      line: { color: "0E7A54", width: 1.75 } });
    s6.addText(t, { x: cx - 0.95, y: y + 0.17, w: 1.9, h: 0.18,
      fontFace: SANS, fontSize: 7.5, italic: true, color: "0E7A54",
      align: "center", margin: 0, isTextBox: true });
  };
  entra(C12, RWB, "entra (refresco 2012, con 0–1 año)");
  s6.addText("Las barras empiezan al NACER; el anillo marca la entrada a la"
    + " ELPI y el punto lleno, la medición que usa la regresión.", {
    x: 2.9, y: 4.62, w: 9.9, h: 0.2, fontFace: SANS, fontSize: 8.5,
    italic: true, color: FAINT, align: "left", margin: 0, isTextBox: true });

  // tarjetas de comparacion
  const card = (x, fill, head, body) => {
    s6.addShape(pptx.ShapeType.roundRect, { x, y: 5.05, w: 3.97, h: 1.8,
      fill: { color: fill }, line: { type: "none" }, rectRadius: 0.07 });
    s6.addText(head, { x: x + 0.16, y: 5.17, w: 3.65, h: 0.24, fontFace: SANS,
      fontSize: 10.5, bold: true, color: NAVY, align: "left", margin: 0,
      isTextBox: true });
    s6.addText(body, { x: x + 0.16, y: 5.45, w: 3.65, h: 1.3, fontFace: SANS,
      fontSize: 9.3, color: MUT, align: "left", margin: 0, isTextBox: true,
      lineSpacingMultiple: 1.05 });
  };
  card(0.5, TINT, "CORTO PLAZO · 2 años",
    "Tratados con 2–6 años (ola 2012) vs. controles con 2–6 años (ola 2017): misma edad, distinta ola — la diferencia de ola la absorbe ηw.");
  card(4.67, TINT, "MEDIANO PLAZO · 7 años",
    "Tratados 7–11 vs. controles 2–6, todos en la ola 2017: misma ola, distinta edad — tests normados por edad (+ z por tramo).");
  card(8.84, "FDE8DC", "LARGO PLAZO · 14 años (nuestro)",
    "Tratados 14–18 en la ola 2024. El control NO fue re-entrevistado: se importa de la ola 2017 (CBCL2, TVIP) — y para PHQ/GAD no existe en ninguna ola.");

  s6.addText(
    "Estructura muestral según ap. T3–T4 de Gillmore (EER 2026) y microdato ELPI. ηw = efecto fijo de ola de la ec. (1).",
    { x: 0.5, y: 7.14, w: 12.33, h: 0.24, fontFace: SANS, fontSize: 8,
      color: FAINT, align: "left", margin: 0, isTextBox: true });
  s6.addNotes("Diagrama del diseno de Gillmore: fila tratada (2006-nov2010) medida en 2012 (2-6, corto), 2017 (7-11, mediano) y 2024 (14-18, largo); filas de control nacidas post-27F via refrescos, medidas en 2017 y NO re-entrevistadas en 2024; banda roja = 27-F.");

  await pptx.writeFile({ fileName: "elpi_gillmore_deck.pptx" });
  console.log("written elpi_gillmore_deck.pptx");
})().catch(e => { console.error(e); process.exit(1); });
