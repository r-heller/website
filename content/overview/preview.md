---
title: "Overview — design preview"
date: 2026-05-06
draft: true
description: "Static no-JS layout preview for sign-off (Phase 2)."
---

> **Static preview only.** No filtering, no search, no live graph.
> Renders dummy nodes at fixed positions so you can judge typography,
> colour, density, and spacing before the interactive layer is built.

<div class="ov-page">

<div class="ov-header">
  <input class="ov-search" type="text" placeholder="Search publications, software, courses…  (preview, inert)" disabled>
  <div class="ov-type-chips">
    <button class="ov-chip" aria-pressed="true">● Publications</button>
    <button class="ov-chip" aria-pressed="true">■ Software</button>
    <button class="ov-chip" aria-pressed="true">▲ Courses</button>
  </div>
</div>

<div class="ov-body">

  <aside class="ov-rail" aria-label="Filters (preview, inert)">
    <h4>Type</h4>
    <div class="ov-chip-group">
      <button class="ov-chip" aria-pressed="true">Publication · 52</button>
      <button class="ov-chip" aria-pressed="true">Software · 10</button>
      <button class="ov-chip" aria-pressed="true">Course · 569</button>
    </div>

    <h4>Research topic</h4>
    <div class="ov-chip-group">
      <button class="ov-chip ov-topic-1"><span class="swatch"></span>TSCI · 18</button>
      <button class="ov-chip ov-topic-2"><span class="swatch"></span>Trace elements · 12</button>
      <button class="ov-chip ov-topic-3"><span class="swatch"></span>COVID · 9</button>
      <button class="ov-chip ov-topic-4"><span class="swatch"></span>Bone regen · 9</button>
      <button class="ov-chip ov-topic-5"><span class="swatch"></span>Ortho trauma · 5</button>
      <button class="ov-chip ov-topic-6"><span class="swatch"></span>Onc / haem · 2</button>
      <button class="ov-chip ov-topic-7"><span class="swatch"></span>Imaging tools · 6</button>
      <button class="ov-chip ov-topic-8"><span class="swatch"></span>R tooling · 4</button>
    </div>

    <h4>Tutorial topic</h4>
    <div class="ov-chip-group">
      <button class="ov-chip">Regression · 51</button>
      <button class="ov-chip">Bioinformatics · 50</button>
      <button class="ov-chip">ML · 46</button>
      <button class="ov-chip">Inference · 45</button>
      <button class="ov-chip">Probability · 40</button>
      <button class="ov-chip">Clinical biostat · 36</button>
      <button class="ov-chip">Visualisation · 35</button>
      <button class="ov-chip">Bayesian · 35</button>
      <button class="ov-chip">… 8 more</button>
    </div>

    <h4>Method</h4>
    <div class="ov-chip-group">
      <button class="ov-chip">ROC / biomarker · 16</button>
      <button class="ov-chip">Time-resolved · 6</button>
      <button class="ov-chip">Logistic regression · 5</button>
      <button class="ov-chip">Mixed-effects · 4</button>
      <button class="ov-chip">Cox regression · 2</button>
      <button class="ov-chip">RNA-seq DE · 1</button>
      <button class="ov-chip">… 8 more</button>
    </div>

    <h4>Year</h4>
    <div style="font-family: var(--ov-mono); font-size: .8rem; color: var(--ov-text-2);">
      2016 ────●──────● 2026 <em>(slider, preview)</em>
    </div>

    <button class="reset" type="button">Reset all</button>
  </aside>

  <section class="ov-graph" aria-label="Network graph (preview)">
    <svg viewBox="0 0 800 500" preserveAspectRatio="xMidYMid meet"
         style="width:100%; height:100%; display:block;">
      <!-- topic-related (dashed, faint) -->
      <g stroke-dasharray="3,3" stroke-opacity="0.15" stroke="currentColor" fill="none">
        <line x1="180" y1="120" x2="240" y2="170"/>
        <line x1="240" y1="170" x2="300" y2="130"/>
        <line x1="300" y1="130" x2="360" y2="180"/>
        <line x1="500" y1="100" x2="560" y2="140"/>
        <line x1="500" y1="100" x2="600" y2="190"/>
        <line x1="600" y1="350" x2="650" y2="390"/>
        <line x1="650" y1="390" x2="700" y2="360"/>
      </g>
      <!-- shared-tags (solid, topic-coloured) -->
      <g stroke-opacity="0.30" fill="none">
        <line x1="240" y1="170" x2="500" y2="100" stroke="var(--ov-t1)" stroke-width="2"/>
        <line x1="300" y1="130" x2="560" y2="140" stroke="var(--ov-t2)" stroke-width="1.5"/>
        <line x1="180" y1="120" x2="600" y2="350" stroke="var(--ov-t3)"/>
        <line x1="360" y1="180" x2="650" y2="390" stroke="var(--ov-t4)"/>
        <line x1="500" y1="100" x2="700" y2="360" stroke="var(--ov-t1)"/>
      </g>
      <!-- used-in (solid, full opacity, with arrow) -->
      <defs>
        <marker id="ov-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
        </marker>
      </defs>
      <line x1="240" y1="170" x2="600" y2="350" stroke="currentColor"
            stroke-width="2.5" marker-end="url(#ov-arrow)"/>

      <!-- Publications: filled circles -->
      <g>
        <circle cx="180" cy="120" r="9" fill="var(--ov-t1)" />
        <circle cx="240" cy="170" r="11" fill="var(--ov-t1)" />
        <circle cx="300" cy="130" r="8" fill="var(--ov-t2)" />
        <circle cx="360" cy="180" r="10" fill="var(--ov-t3)" />
        <circle cx="500" cy="100" r="9" fill="var(--ov-t4)" />
        <circle cx="560" cy="140" r="8" fill="var(--ov-t5)" />
      </g>

      <!-- Software: rounded squares -->
      <g>
        <rect x="592" y="182" width="16" height="16" rx="3" fill="var(--ov-t7)" />
        <rect x="650" y="232" width="16" height="16" rx="3" fill="var(--ov-t8)" />
        <rect x="270" y="240" width="16" height="16" rx="3" fill="var(--ov-t1)" />
      </g>

      <!-- Courses: triangles (compound clusters in real graph) -->
      <g>
        <polygon points="600,350 608,338 592,338" fill="var(--ov-t2)" />
        <polygon points="650,390 658,378 642,378" fill="var(--ov-t3)" />
        <polygon points="700,360 708,348 692,348" fill="var(--ov-t4)" />
        <polygon points="430,300 438,288 422,288" fill="var(--ov-t5)" />
        <polygon points="470,360 478,348 462,348" fill="var(--ov-t6)" />
        <polygon points="380,400 388,388 372,388" fill="var(--ov-t1)" />
        <polygon points="520,420 528,408 512,408" fill="var(--ov-t2)" />
      </g>
    </svg>
    <div class="placeholder">cytoscape canvas mounts here in Phase 3</div>
  </section>

</div>

<div class="ov-stats">
  <span><strong>52</strong> publications</span>
  <span><strong>10</strong> software</span>
  <span><strong>569</strong> courses shown</span>
  <span style="margin-left:auto;">2 440 edges · 100% coverage</span>
</div>

<div class="ov-lists">

  <div class="ov-col">
    <h3>Publications <span class="count">52</span></h3>

    <article class="ov-card ov-topic-1">
      <div class="ov-card-title"><span class="ov-glyph ov-pub"></span>Predicting neurological recovery after traumatic spinal cord injury by time-resolved analysis of monocyte subsets</div>
      <div class="ov-card-meta">Heller R, Seelig J, et al · 2021 · <em>Brain</em></div>
      <div class="ov-card-tags">
        <span class="ov-tag">trauma-spinal-cord-injury</span>
        <span class="ov-tag">time-resolved</span>
        <span class="ov-tag">mixed-effects</span>
      </div>
      <a class="ov-card-link" href="#">DOI ↗</a>
    </article>

    <article class="ov-card ov-topic-3">
      <div class="ov-card-title"><span class="ov-glyph ov-pub"></span>Prediction of Survival Odds in COVID-19 by Zinc, Age and Selenoprotein P as Composite Biomarker</div>
      <div class="ov-card-meta">Heller R, Sun Q, et al · 2020 · <em>Redox Biology</em></div>
      <div class="ov-card-tags">
        <span class="ov-tag">covid-19</span>
        <span class="ov-tag">trace-elements</span>
        <span class="ov-tag">logistic-regression</span>
        <span class="ov-tag">roc</span>
      </div>
      <a class="ov-card-link" href="#">DOI ↗</a>
    </article>

    <article class="ov-card ov-topic-4">
      <div class="ov-card-title"><span class="ov-glyph ov-pub"></span>Evaluation of the Clinical Effectiveness of Bioactive Glass (S53P4) in the Treatment of Non-Unions: Study Protocol RCT</div>
      <div class="ov-card-meta">Tanner MC, Heller R, et al · 2018 · <em>Trials</em></div>
      <div class="ov-card-tags">
        <span class="ov-tag">bone-regeneration</span>
        <span class="ov-tag">clinical-trial-design</span>
      </div>
      <a class="ov-card-link" href="#">DOI ↗</a>
    </article>

    <div style="text-align:center; color: var(--ov-text-2); font-size:.8rem; padding:.5rem 0;">
      … 49 more (scroll)
    </div>
  </div>

  <div class="ov-col">
    <h3>Software <span class="count">10</span></h3>

    <article class="ov-card ov-topic-7">
      <div class="ov-card-title"><span class="ov-glyph ov-sw"></span>bambamR</div>
      <div class="ov-card-meta">R · molecular-and-imaging-tools</div>
      <div class="ov-card-tags">
        <span class="ov-tag">rna-seq</span>
        <span class="ov-tag">deseq2</span>
      </div>
      <a class="ov-card-link" href="#">GitHub ↗</a>
    </article>

    <article class="ov-card ov-topic-7">
      <div class="ov-card-title"><span class="ov-glyph ov-sw"></span>phenoscapR</div>
      <div class="ov-card-meta">R · molecular-and-imaging-tools</div>
      <div class="ov-card-tags">
        <span class="ov-tag">codex</span>
        <span class="ov-tag">spatial</span>
      </div>
      <a class="ov-card-link" href="#">GitHub ↗</a>
    </article>

    <article class="ov-card ov-topic-1">
      <div class="ov-card-title"><span class="ov-glyph ov-sw"></span>scimagR</div>
      <div class="ov-card-meta">R · trauma-spinal-cord-injury</div>
      <div class="ov-card-tags">
        <span class="ov-tag">mri</span>
        <span class="ov-tag">segmentation</span>
      </div>
      <a class="ov-card-link" href="#">GitHub ↗</a>
    </article>

    <article class="ov-card ov-topic-8">
      <div class="ov-card-title"><span class="ov-glyph ov-sw"></span>lstparsR</div>
      <div class="ov-card-meta">R · biostatistics-research-methods</div>
      <div class="ov-card-tags">
        <span class="ov-tag">nonmem</span>
        <span class="ov-tag">pkpd</span>
      </div>
      <a class="ov-card-link" href="#">GitHub ↗</a>
    </article>

    <div style="text-align:center; color: var(--ov-text-2); font-size:.8rem; padding:.5rem 0;">
      … 6 more (scroll)
    </div>
  </div>

  <div class="ov-col">
    <h3>Courses <span class="count">569</span></h3>

    <article class="ov-card ov-topic-2">
      <div class="ov-card-title"><span class="ov-glyph ov-course"></span>Variant Annotation with VEP</div>
      <div class="ov-card-meta">CTTIR · bioinformatics</div>
      <div class="ov-card-tags">
        <span class="ov-tag">vep</span>
        <span class="ov-tag">annotation</span>
      </div>
      <a class="ov-card-link" href="#">CTTIR ↗</a>
    </article>

    <article class="ov-card ov-topic-6">
      <div class="ov-card-title"><span class="ov-glyph ov-course"></span>Bayes Factors</div>
      <div class="ov-card-meta">CTTIR · bayesian</div>
      <div class="ov-card-tags">
        <span class="ov-tag">model-comparison</span>
      </div>
      <a class="ov-card-link" href="#">CTTIR ↗</a>
    </article>

    <article class="ov-card ov-topic-3">
      <div class="ov-card-title"><span class="ov-glyph ov-course"></span>Cooks distance</div>
      <div class="ov-card-meta">CTTIR · regression-modelling</div>
      <div class="ov-card-tags">
        <span class="ov-tag">diagnostics</span>
      </div>
      <a class="ov-card-link" href="#">CTTIR ↗</a>
    </article>

    <article class="ov-card ov-topic-7">
      <div class="ov-card-title"><span class="ov-glyph ov-course"></span>Cox proportional hazards</div>
      <div class="ov-card-meta">CTTIR · survival-analysis</div>
      <div class="ov-card-tags">
        <span class="ov-tag">cox</span>
        <span class="ov-tag">hazard-ratio</span>
      </div>
      <a class="ov-card-link" href="#">CTTIR ↗</a>
    </article>

    <div style="text-align:center; color: var(--ov-text-2); font-size:.8rem; padding:.5rem 0;">
      … 565 more (scroll)
    </div>
  </div>

</div>

</div>
