---
title: "2. Data Visualisation with ggplot2"
date: 2026-03-05
description: "Create publication-ready plots with ggplot2 — from histograms and boxplots to complex multi-panel figures."
tags: ["R", "ggplot2", "visualisation"]
weight: 2
---

Good visualisation is the backbone of data analysis. R's `ggplot2` package implements the **grammar of graphics**, giving you a flexible, layered system for building any plot you can imagine.

## Setup

```r
library(tidyverse)
data(mtcars)
mtcars$cyl <- factor(mtcars$cyl)
```

## The Grammar of Graphics

Every ggplot has three essential components:

1. **Data** — the data frame
2. **Aesthetics** (`aes()`) — mappings from variables to visual properties
3. **Geometries** (`geom_*`) — the type of plot

```r
ggplot(data = mtcars, aes(x = mpg)) +
  geom_histogram(binwidth = 2, fill = "steelblue", colour = "white") +
  labs(title = "Distribution of MPG", x = "Miles per Gallon", y = "Count") +
  theme_minimal()
```

## Histogram and Density Plots

```r
# Density plot
ggplot(mtcars, aes(x = mpg, fill = cyl)) +
  geom_density(alpha = 0.5) +
  labs(title = "MPG Density by Cylinder Count", fill = "Cylinders") +
  theme_minimal()
```

## Boxplots

```r
ggplot(mtcars, aes(x = cyl, y = mpg, fill = cyl)) +
  geom_boxplot(outlier.colour = "red") +
  labs(title = "MPG by Number of Cylinders", x = "Cylinders", y = "MPG") +
  theme_minimal() +
  theme(legend.position = "none")
```

## Violin Plots

```r
ggplot(mtcars, aes(x = cyl, y = mpg, fill = cyl)) +
  geom_violin(trim = FALSE) +
  geom_jitter(width = 0.1, alpha = 0.5) +
  labs(title = "MPG Distribution by Cylinders") +
  theme_minimal() +
  theme(legend.position = "none")
```

## Scatterplots

```r
ggplot(mtcars, aes(x = wt, y = mpg, colour = cyl)) +
  geom_point(size = 3) +
  geom_smooth(method = "lm", se = TRUE) +
  labs(
    title = "Weight vs. MPG",
    x = "Weight (1000 lbs)",
    y = "Miles per Gallon",
    colour = "Cylinders"
  ) +
  theme_minimal()
```

## Bar Charts

```r
# Count-based
ggplot(mtcars, aes(x = cyl, fill = cyl)) +
  geom_bar() +
  labs(title = "Number of Cars by Cylinder Count") +
  theme_minimal() +
  theme(legend.position = "none")

# Summary-based
mtcars %>%
  group_by(cyl) %>%
  summarise(mean_mpg = mean(mpg), se = sd(mpg) / sqrt(n())) %>%
  ggplot(aes(x = cyl, y = mean_mpg, fill = cyl)) +
  geom_col() +
  geom_errorbar(aes(ymin = mean_mpg - se, ymax = mean_mpg + se), width = 0.2) +
  labs(title = "Mean MPG by Cylinders (± SE)") +
  theme_minimal() +
  theme(legend.position = "none")
```

## Faceted Plots

```r
ggplot(mtcars, aes(x = wt, y = mpg)) +
  geom_point() +
  geom_smooth(method = "lm") +
  facet_wrap(~ cyl, scales = "free") +
  labs(title = "Weight vs. MPG by Cylinder Count") +
  theme_minimal()
```

## Correlation Heatmap

```r
library(reshape2)

cor_matrix <- cor(mtcars[, sapply(mtcars, is.numeric)])
melted_cor <- melt(cor_matrix)

ggplot(melted_cor, aes(x = Var1, y = Var2, fill = value)) +
  geom_tile() +
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", midpoint = 0) +
  labs(title = "Correlation Heatmap") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
```

## Customising Themes

```r
# Create a custom theme for publications
theme_publication <- function() {
  theme_minimal() +
    theme(
      text = element_text(family = "sans", size = 12),
      plot.title = element_text(face = "bold", size = 14),
      axis.title = element_text(face = "bold"),
      legend.position = "bottom",
      panel.grid.minor = element_blank()
    )
}

# Apply it
ggplot(mtcars, aes(x = wt, y = mpg)) +
  geom_point(aes(colour = cyl), size = 3) +
  labs(title = "Publication-Ready Scatterplot") +
  theme_publication()
```

## Saving Plots

```r
p <- ggplot(mtcars, aes(x = wt, y = mpg)) + geom_point() + theme_minimal()
ggsave("my_plot.png", p, width = 8, height = 5, dpi = 300)
ggsave("my_plot.pdf", p, width = 8, height = 5)
```

## Key Takeaways

- Use `ggplot2` for all your plotting needs — it is the gold standard in R.
- Build plots in layers: data → aesthetics → geometry → labels → theme.
- Use facets for multi-panel plots comparing groups.
- Create a custom theme for consistent, publication-ready figures.

**Previous:** [← Descriptive Statistics]({{< ref "01-descriptive-statistics" >}})
**Next:** [Inferential Statistics →]({{< ref "03-inferential-statistics" >}})
