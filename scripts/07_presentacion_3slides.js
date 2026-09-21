// 3-slide deck: ELPI overview / sampling evolution / Gillmore specification
const pptxgen = require("pptxgenjs") // npm i pptxgenjs react-icons react react-dom sharp;
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
  // SLIDE 3 — Gillmore specification (economic-seminar slide)
  // =====================================================================
  const s3 = pptx.addSlide();
  s3.background = { color: "FFFFFF" };

  s3.addText("Empirical strategy — Gillmore (2025)", {
    x: 0.5, y: 0.26, w: 12.33, h: 0.54, fontFace: SER, fontSize: 30, bold: true,
    color: INK, align: "left", margin: 0, isTextBox: true,
  });
  s3.addText(
    "Difference-in-differences: municipal seismic intensity × birth-cohort exposure to the 2010 Chilean earthquake (27-F). “Natural Disasters and Early Child Development: Evidence from an Earthquake.”",
    { x: 0.5, y: 0.88, w: 12.33, h: 0.34, fontFace: SANS, fontSize: 12, color: MUT,
      align: "left", margin: 0, isTextBox: true }
  );

  // equation panel
  s3.addShape(pptx.ShapeType.roundRect, {
    x: 0.5, y: 1.42, w: 12.33, h: 1.06, fill: { color: TINT }, line: { type: "none" }, rectRadius: 0.07,
  });
  const it = { italic: true };
  const sub = { italic: true, subscript: true };
  const eq = [
    { text: "Y", options: { ...it } }, { text: "ijtw", options: { ...sub } },
    { text: " = ", options: {} },
    { text: "β", options: { bold: true, color: ORANGE } },
    { text: " (Affected", options: { ...it, color: NAVY, bold: true } },
    { text: "it", options: { ...sub, color: NAVY, bold: true } },
    { text: " × Mercalli", options: { ...it, color: NAVY, bold: true } },
    { text: "j", options: { ...sub, color: NAVY, bold: true } },
    { text: ")", options: { color: NAVY, bold: true } },
    { text: " + γ", options: {} },
    { text: " Affected", options: { ...it } }, { text: "it", options: { ...sub } },
    { text: " + X", options: { ...it } }, { text: "ijt", options: { ...sub } },
    { text: " + ψ", options: {} }, { text: "j", options: { ...sub } },
    { text: " + θ", options: {} }, { text: "t", options: { ...sub } },
    { text: " + λ", options: {} }, { text: "jt", options: { ...sub } },
    { text: " + η", options: {} }, { text: "w", options: { ...sub } },
    { text: " + e", options: { ...it } }, { text: "ijtw", options: { ...sub } },
  ];
  s3.addText(eq, {
    x: 0.8, y: 1.42, w: 11.0, h: 1.06, fontFace: SER, fontSize: 20, color: INK,
    align: "center", valign: "middle", margin: 0, isTextBox: true,
  });
  s3.addText("(2.1)", {
    x: 11.9, y: 1.42, w: 0.8, h: 1.06, fontFace: SER, fontSize: 13, color: FAINT,
    align: "right", valign: "middle", margin: 0, isTextBox: true,
  });

  // definitions, two columns
  const defLine = (term, sfx, rest) => {
    const runs = [{ text: term, options: { italic: true, bold: true, color: NAVY, fontFace: SER, fontSize: 12 } }];
    if (sfx) runs.push({ text: sfx, options: { italic: true, bold: true, color: NAVY, subscript: true, fontFace: SER, fontSize: 12 } });
    runs.push({ text: "  " + rest, options: { color: INK, fontSize: 10.8 } });
    return runs;
  };
  const colOpts = (x) => ({
    x, y: 2.68, w: 5.95, h: 2.28, fontFace: SANS, align: "left", valign: "top",
    margin: 0, isTextBox: true, paraSpaceAfter: 7,
  });
  const L = [
    defLine("i, j, t, w", "", "child · municipality · birth cohort · survey wave (2012, 2017)"),
    defLine("Affected", "it", "= 1 if child i of cohort t was conceived before 27-F — between in utero and age 5 at impact (exposed cohorts vs. cohorts conceived after)"),
    defLine("Mercalli", "j", "modified Mercalli intensity of municipality j (Astroza et al. 2010: housing damage conditional on construction type; robustness: USGS peak ground acceleration)"),
    defLine("X", "ijt", "child, mother & household controls, incl. pre-earthquake characteristics"),
  ];
  const R = [
    defLine("ψ", "j", "municipality fixed effects"),
    defLine("θ", "t", "birth-cohort fixed effects"),
    defLine("η", "w", "survey-wave fixed effects"),
    defLine("λ", "jt", "municipality-specific linear trends — allow stable differential trends in development across municipalities"),
    defLine("e", "ijtw", "error term; standard errors clustered at the municipality level"),
  ];
  const flat = (arr) => arr.flatMap((runs, k) => {
    const out = runs.map(r => ({ ...r }));
    out[out.length - 1].options = { ...out[out.length - 1].options, breakLine: k < arr.length - 1 };
    return out;
  });
  s3.addText(flat(L), colOpts(0.5));
  s3.addText(flat(R), colOpts(6.88));

  // identification + threats band
  s3.addShape(pptx.ShapeType.roundRect, {
    x: 0.5, y: 5.12, w: 7.3, h: 1.72, fill: { color: NAVY }, line: { type: "none" }, rectRadius: 0.07,
  });
  s3.addText([
    { text: "Identification.  ", options: { bold: true, color: "FFFFFF" } },
    { text: "β", options: { bold: true, color: "FFC9A8", fontFace: SER, italic: true } },
    { text: " = intention-to-treat: effect of one additional Mercalli unit on exposed cohorts. Assumption: absent 27-F, exposed cohorts would have trended like post-earthquake cohorts within each municipality (parallel trends conditional on λ", options: { color: "FFFFFF" } },
    { text: "jt", options: { color: "FFFFFF", subscript: true, italic: true } },
    { text: "). Post-quake conceptions may be indirectly exposed (stress, income) → ", options: { color: "FFFFFF" } },
    { text: "β is a lower bound.", options: { bold: true, color: "FFC9A8" } },
  ], {
    x: 0.75, y: 5.28, w: 6.8, h: 1.4, fontFace: SANS, fontSize: 11, align: "left",
    valign: "top", margin: 0, isTextBox: true, lineSpacingMultiple: 1.12,
  });
  s3.addShape(pptx.ShapeType.roundRect, {
    x: 8.05, y: 5.12, w: 4.78, h: 1.72, fill: { color: CARD }, line: { type: "none" }, rectRadius: 0.07,
  });
  s3.addText([
    { text: "Threats addressed", options: { bold: true, color: NAVY, breakLine: true, fontSize: 11 } },
    { text: "Placebo on post-quake cohorts: null", options: { bullet: true, color: MUT, breakLine: true } },
    { text: "Migration between waves 0.78% (affected → unaffected: 0.02%)", options: { bullet: true, color: MUT, breakLine: true } },
    { text: "Fertility, planned births & sex ratio: null in vital records", options: { bullet: true, color: MUT, breakLine: true } },
    { text: "Attrition uncorrelated with intensity", options: { bullet: true, color: MUT } },
  ], {
    x: 8.3, y: 5.26, w: 4.35, h: 1.46, fontFace: SANS, fontSize: 10, align: "left",
    valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 4,
  });

  s3.addText(
    "Eq. (2.1) as in Gillmore, UT Austin dissertation (2023), ch. 2; SSRN WP 5106675 (2025); Economics of Education Review (2026). The published version defines exposure as prenatal to age 4. Outcomes: TVIP/Peabody, Battelle, CBCL.",
    { x: 0.5, y: 7.06, w: 12.33, h: 0.34, fontFace: SANS, fontSize: 8, color: FAINT,
      align: "left", margin: 0, isTextBox: true }
  );
  s3.addNotes("Specification slide only, per request: eq. (2.1) verbatim from the dissertation chapter; beta highlighted; definitions; identification assumption incl. lower-bound argument (footnote 3); validity checks summarized.");

  await pptx.writeFile({ fileName: "elpi_gillmore_3slides.pptx" });
  console.log("written elpi_gillmore_3slides.pptx");
})().catch(e => { console.error(e); process.exit(1); });
