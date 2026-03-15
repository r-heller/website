---
title: "1. Descriptive Statistics in R"
date: 2026-03-01
description: "Learn to summarise and explore data using measures of central tendency, dispersion, and distribution shape."
tags: ["R", "statistics", "descriptive"]
weight: 1
---

Descriptive statistics give you a first look at your data. Before running any model, you need to understand the shape, centre, and spread of your variables.

## Setup

```r
library(tidyverse)

# We'll use the built-in mtcars dataset
data(mtcars)
head(mtcars)
```

## Measures of Central Tendency

### Mean, Median, Mode

```r
# Mean
mean(mtcars$mpg)

# Median
median(mtcars$mpg)

# Mode (no built-in function)
get_mode <- function(x) {
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}
get_mode(mtcars$cyl)
```

### When to use which?

| Measure | Best for | Sensitive to outliers? |
|---------|----------|----------------------|
| Mean    | Symmetric distributions | Yes |
| Median  | Skewed distributions | No |
| Mode    | Categorical data | No |

## Measures of Dispersion

```r
# Standard deviation
sd(mtcars$mpg)

# Variance
var(mtcars$mpg)

# Range
range(mtcars$mpg)
diff(range(mtcars$mpg))

# Interquartile range
IQR(mtcars$mpg)

# Quantiles
quantile(mtcars$mpg, probs = c(0.25, 0.5, 0.75))
```

## Summary Statistics at a Glance

```r
# Base R summary
summary(mtcars$mpg)

# More detailed summary with psych package
# install.packages("psych")
library(psych)
describe(mtcars$mpg)
```

## Frequency Tables

```r
# For categorical/discrete variables
table(mtcars$cyl)

# Proportions
prop.table(table(mtcars$cyl))

# Cross-tabulation
table(mtcars$cyl, mtcars$gear)
```

## Group-wise Summaries

```r
mtcars %>%
  group_by(cyl) %>%
  summarise(
    n       = n(),
    mean_mpg = mean(mpg),
    sd_mpg   = sd(mpg),
    median_mpg = median(mpg),
    min_mpg  = min(mpg),
    max_mpg  = max(mpg)
  )
```

## Checking Normality

```r
# Shapiro-Wilk test
shapiro.test(mtcars$mpg)

# Q-Q plot
qqnorm(mtcars$mpg)
qqline(mtcars$mpg, col = "red")
```

## Skewness and Kurtosis

```r
library(moments)
# install.packages("moments")

skewness(mtcars$mpg)
kurtosis(mtcars$mpg)
```

A skewness near 0 indicates symmetry. Kurtosis near 3 indicates a normal-like tail weight (excess kurtosis near 0).

## Key Takeaways

- Always start with descriptive statistics before modelling.
- Use `summary()` and `describe()` for a quick overview.
- Check normality with Shapiro-Wilk and Q-Q plots.
- Group-wise summaries using `dplyr` reveal differences across subgroups.

**Next:** [Data Visualisation →]({{< ref "02-data-visualisation" >}})
