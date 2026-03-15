---
title: "R Statistics Tutorials"
description: "A structured learning path from descriptive statistics to advanced modelling in R."
---

Welcome to the **R Statistics Tutorial Series**. This curriculum is designed to take you from summarising raw data all the way to building and interpreting complex statistical models — with beautiful visualisations along the way.

Each tutorial includes fully reproducible R code that you can copy and run in your own R environment.

## Learning Path

| # | Tutorial | Topics |
|---|----------|--------|
| 1 | [Descriptive Statistics]({{< ref "01-descriptive-statistics" >}}) | Mean, median, SD, quantiles, frequency tables |
| 2 | [Data Visualisation]({{< ref "02-data-visualisation" >}}) | ggplot2, histograms, boxplots, scatterplots |
| 3 | [Inferential Statistics]({{< ref "03-inferential-statistics" >}}) | t-tests, ANOVA, chi-square, non-parametric tests |
| 4 | [Regression & Modelling]({{< ref "04-regression-modelling" >}}) | Linear models, GLM, mixed models, diagnostics |

## Prerequisites

- **R** (version 4.0+) installed — [Download R](https://cran.r-project.org/)
- **RStudio** recommended — [Download RStudio](https://posit.co/download/rstudio-desktop/)
- Packages used throughout: `tidyverse`, `ggplot2`, `car`, `lme4`

```r
# Install all required packages
install.packages(c("tidyverse", "ggplot2", "car", "lme4", "broom"))
```
