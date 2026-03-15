---
title: "4. Regression & Statistical Modelling in R"
date: 2026-03-12
description: "Linear regression, multiple regression, generalised linear models, mixed-effects models, and model diagnostics."
tags: ["R", "regression", "modelling", "GLM", "mixed models"]
weight: 4
---

Statistical models let you quantify relationships between variables, make predictions, and test hypotheses about causal mechanisms. This tutorial covers the modelling workflow from simple linear regression to mixed-effects models.

## Setup

```r
library(tidyverse)
library(broom)
data(mtcars)
```

## Simple Linear Regression

```r
# Does weight predict MPG?
model1 <- lm(mpg ~ wt, data = mtcars)
summary(model1)
```

### Interpreting the Output

- **Intercept (β₀):** Expected MPG when weight = 0 (extrapolation)
- **Slope (β₁):** For each 1000 lb increase in weight, MPG changes by β₁
- **R²:** Proportion of variance in MPG explained by weight
- **p-value:** Probability of observing this slope if the true slope were 0

### Tidy Output with `broom`

```r
tidy(model1)        # Coefficient table
glance(model1)      # Model-level statistics
augment(model1)     # Observation-level statistics (fitted, residuals)
```

## Multiple Regression

```r
model2 <- lm(mpg ~ wt + hp + cyl, data = mtcars)
summary(model2)

# Compare models
anova(model1, model2)
AIC(model1, model2)
BIC(model1, model2)
```

### Multicollinearity

```r
library(car)

# Variance Inflation Factors
vif(model2)
# VIF > 5 suggests problematic collinearity
```

## Model Diagnostics

```r
# Diagnostic plots
par(mfrow = c(2, 2))
plot(model2)
```

### What to look for:

1. **Residuals vs Fitted:** Should show no pattern (linearity)
2. **Q-Q Plot:** Points should follow the diagonal (normality)
3. **Scale-Location:** Horizontal band (homoscedasticity)
4. **Residuals vs Leverage:** Identify influential observations

```r
# Formal tests
# Normality of residuals
shapiro.test(residuals(model2))

# Homoscedasticity (Breusch-Pagan)
library(lmtest)
bptest(model2)

# Autocorrelation (Durbin-Watson)
dwtest(model2)
```

## Interaction Effects

```r
model3 <- lm(mpg ~ wt * factor(cyl), data = mtcars)
summary(model3)

# Visualise interaction
ggplot(mtcars, aes(x = wt, y = mpg, colour = factor(cyl))) +
  geom_point(size = 3) +
  geom_smooth(method = "lm", se = TRUE) +
  labs(title = "Weight × Cylinders Interaction",
       colour = "Cylinders") +
  theme_minimal()
```

## Polynomial Regression

```r
model_poly <- lm(mpg ~ poly(wt, 2), data = mtcars)
summary(model_poly)

ggplot(mtcars, aes(x = wt, y = mpg)) +
  geom_point() +
  geom_smooth(method = "lm", formula = y ~ poly(x, 2), colour = "red") +
  labs(title = "Quadratic Fit: Weight vs MPG") +
  theme_minimal()
```

## Generalised Linear Models (GLM)

### Logistic Regression

```r
# Predict transmission type (0 = automatic, 1 = manual)
model_logit <- glm(am ~ wt + hp, data = mtcars, family = binomial)
summary(model_logit)

# Odds ratios
exp(coef(model_logit))
exp(confint(model_logit))
```

### Poisson Regression

```r
# Count data example
model_pois <- glm(carb ~ wt + hp, data = mtcars, family = poisson)
summary(model_pois)

# Check for overdispersion
deviance(model_pois) / df.residual(model_pois)
# Values >> 1 indicate overdispersion
```

## Mixed-Effects Models

When data has a hierarchical or grouped structure (e.g., students within schools, measurements within subjects):

```r
library(lme4)

# Using sleepstudy dataset (reaction time over days of sleep deprivation)
data(sleepstudy)

# Random intercept model
mixed1 <- lmer(Reaction ~ Days + (1 | Subject), data = sleepstudy)
summary(mixed1)

# Random intercept and slope
mixed2 <- lmer(Reaction ~ Days + (Days | Subject), data = sleepstudy)
summary(mixed2)

# Compare models
anova(mixed1, mixed2)
```

### Visualising Random Effects

```r
# Plot individual trajectories
ggplot(sleepstudy, aes(x = Days, y = Reaction, group = Subject)) +
  geom_line(alpha = 0.3) +
  geom_smooth(aes(group = 1), method = "lm", colour = "red", linewidth = 1.5) +
  labs(title = "Reaction Time Over Sleep Deprivation Days",
       subtitle = "Grey = individual subjects, Red = population average") +
  theme_minimal()

# Extract and plot random effects
ranef_df <- as.data.frame(ranef(mixed2)$Subject)
ranef_df$Subject <- rownames(ranef_df)

ggplot(ranef_df, aes(x = `(Intercept)`, y = Days)) +
  geom_point() +
  geom_hline(yintercept = 0, linetype = "dashed") +
  geom_vline(xintercept = 0, linetype = "dashed") +
  labs(title = "Random Effects: Intercept vs Slope",
       x = "Random Intercept", y = "Random Slope") +
  theme_minimal()
```

## Model Selection Workflow

```r
# Step 1: Full model
full_model <- lm(mpg ~ wt + hp + disp + drat + qsec, data = mtcars)

# Step 2: Stepwise selection (use with caution)
step_model <- step(full_model, direction = "both")
summary(step_model)

# Step 3: Compare with AIC/BIC
AIC(model1, model2, full_model, step_model)
```

## Reporting Results

When reporting regression results:

- **Unstandardised coefficients** (β) with 95% CIs
- **p-values** for each predictor
- **R²** (or pseudo-R² for GLMs)
- **F-statistic** and its p-value (for overall model significance)
- **Sample size** (N)

```r
# Create a publication-ready table
library(broom)
model2 %>%
  tidy(conf.int = TRUE) %>%
  mutate(across(where(is.numeric), ~ round(., 3)))
```

## Key Takeaways

- Always check model assumptions with diagnostic plots.
- Use `broom` for tidy model output.
- Choose GLMs when the response variable is not continuous/normal.
- Use mixed models for grouped/hierarchical data.
- Report effect sizes and confidence intervals, not just p-values.

**Previous:** [← Inferential Statistics]({{< ref "03-inferential-statistics" >}})
