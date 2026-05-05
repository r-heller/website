---
title: "3. Inferential Statistics in R"
date: 2026-03-08
description: "Hypothesis testing, confidence intervals, t-tests, ANOVA, chi-square tests, and non-parametric alternatives."
tags: ["R", "statistics", "inferential", "hypothesis testing"]
weight: 3
---

Inferential statistics let you draw conclusions about a population based on sample data. This tutorial covers the most common hypothesis tests and when to use each one.

## Setup

```r
library(tidyverse)
data(mtcars)
mtcars$cyl <- factor(mtcars$cyl)
```

## The Logic of Hypothesis Testing

1. State null hypothesis (H₀) and alternative hypothesis (H₁)
2. Choose a significance level (α, typically 0.05)
3. Compute the test statistic
4. Determine the p-value
5. Reject or fail to reject H₀

> **Remember:** A p-value is NOT the probability that H₀ is true. It is the probability of observing data at least as extreme as yours, assuming H₀ is true.

## One-Sample t-Test

*Is the population mean different from a specific value?*

```r
# Test whether mean MPG differs from 20
t.test(mtcars$mpg, mu = 20)
```

## Two-Sample t-Test

*Do two groups differ in their means?*

```r
# Compare MPG between 4-cylinder and 8-cylinder cars
four_cyl <- mtcars$mpg[mtcars$cyl == "4"]
eight_cyl <- mtcars$mpg[mtcars$cyl == "8"]

# Independent samples t-test (Welch's, default)
t.test(four_cyl, eight_cyl)

# Equal variance assumed (Student's t-test)
t.test(four_cyl, eight_cyl, var.equal = TRUE)
```

### Checking Assumptions

```r
# Normality
shapiro.test(four_cyl)
shapiro.test(eight_cyl)

# Equal variances (Levene's test)
library(car)
leveneTest(mpg ~ cyl, data = mtcars %>% filter(cyl %in% c("4", "8")))
```

## Paired t-Test

```r
# Example with simulated before/after data
set.seed(42)
before <- rnorm(30, mean = 100, sd = 15)
after <- before + rnorm(30, mean = 5, sd = 8)

t.test(before, after, paired = TRUE)
```

## One-Way ANOVA

*Compare means across 3+ groups.*

```r
# Does MPG differ across cylinder groups?
aov_model <- aov(mpg ~ cyl, data = mtcars)
summary(aov_model)
```

### Post-Hoc Tests

```r
# Tukey's HSD for pairwise comparisons
TukeyHSD(aov_model)

# Visualise
plot(TukeyHSD(aov_model))
```

### Checking ANOVA Assumptions

```r
# Residual plots
par(mfrow = c(2, 2))
plot(aov_model)

# Levene's test for homogeneity of variances
leveneTest(mpg ~ cyl, data = mtcars)
```

## Two-Way ANOVA

```r
mtcars$gear <- factor(mtcars$gear)

aov_two <- aov(mpg ~ cyl * gear, data = mtcars)
summary(aov_two)

# Interaction plot
interaction.plot(mtcars$cyl, mtcars$gear, mtcars$mpg,
                 col = 1:3, lwd = 2, type = "b",
                 xlab = "Cylinders", ylab = "Mean MPG",
                 trace.label = "Gears")
```

## Chi-Square Test

*Test association between two categorical variables.*

```r
# Are cylinders and transmission type (am) related?
tab <- table(mtcars$cyl, mtcars$am)
tab

chisq.test(tab)
```

## Non-Parametric Alternatives

When normality assumptions are violated:

| Parametric Test | Non-Parametric Alternative | R Function |
|----------------|---------------------------|------------|
| One-sample t | Wilcoxon signed-rank | `wilcox.test(x, mu = ...)` |
| Two-sample t | Mann-Whitney U | `wilcox.test(x, y)` |
| Paired t | Wilcoxon signed-rank | `wilcox.test(x, y, paired = TRUE)` |
| One-way ANOVA | Kruskal-Wallis | `kruskal.test()` |

```r
# Kruskal-Wallis test
kruskal.test(mpg ~ cyl, data = mtcars)

# Mann-Whitney U test
wilcox.test(four_cyl, eight_cyl)
```

## Effect Sizes

```r
# Cohen's d for t-test
library(effectsize)
# install.packages("effectsize")
cohens_d(four_cyl, eight_cyl)

# Eta-squared for ANOVA
eta_squared(aov_model)
```

## Confidence Intervals

```r
# CI for a mean
t.test(mtcars$mpg)$conf.int

# CI for a proportion
prop.test(sum(mtcars$am), nrow(mtcars))
```

## Key Takeaways

- Always check assumptions before choosing a test.
- Use Welch's t-test (the default) unless you have good reason to assume equal variances.
- Report effect sizes alongside p-values — statistical significance ≠ practical significance.
- When assumptions are violated, use non-parametric alternatives.

**Previous:** [← Data Visualisation]({{< ref "02-data-visualisation" >}})
**Next:** [Regression & Modelling →]({{< ref "04-regression-modelling" >}})
