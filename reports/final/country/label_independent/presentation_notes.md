# Country figures and speaking notes — Yuwei

**Ready for Liwen's independent review; final team approval pending.**
The presentation duration is unconfirmed. The three optional beats below can be shortened
or combined; they do not assume a fixed speaking slot. No reviewed polarity or model result
is implied. UK includes the one Scotland record in every figure.

## Suggested main figure: country coverage

Use `figures/01_country_coverage.png` (editable vector: the matching `.svg`).
Denominator: all 710 retained posts. The top five groups contain 594 posts (83.7%).

Speaking draft:
> We first checked whether country groups were comparable. Most of the sample comes from
> five countries, and their observed dates differ. More than half the USA, UK and Canada
> records are dated 2023, compared with one fifth for Australia. These are properties of our
> synthetic sample, not the countries' populations. We therefore checked comparable date windows.

Backup: `02_2023_monthly_support.png` shows that India stops in May and Australia in June,
while USA/UK/Canada extend into October. The outlined January–April window uses the same
calendar restriction for every group, without implying complete sampling.

## Suggested main figure: distributions

Use `figures/03_interaction_distributions.png`.
Denominators: USA 184, UK 141, Canada 131, Australia 70, India 68.
Boxes span Q1–Q3; whiskers are observed minimum/maximum; diamonds are means, not uncertainty intervals.

Speaking draft:
> The distributions overlap. USA has the largest mean, about 66.8 interactions per post,
> but Canada has the largest median, 63. This difference between the mean and the median
> is why we show the full distributions rather than one ranking. Likes plus retweets are
> recorded counts; we do not have impressions to calculate an engagement rate.

Backup: `05_within_platform.png`; colored point = median, thick line = IQR, hollow diamond = mean.
All 15 full-period cells have at least 19 posts. IQR bars are not confidence intervals.

## Suggested main figure: time-window sensitivity

Use `figures/04_time_window_sensitivity.png`.
Every mean has a matching post count in the second panel; the windows overlap.

Speaking draft:
> Some patterns persist and others do not. USA keeps the largest mean in our five date
> views and in all three full-period platform comparisons. But UK and Canada change order
> when 2023 is excluded. A shared platform mix changes each mean by less than 0.17 interactions,
> so that particular adjustment barely moves the results. We retain both this null check
> and the unstable rankings, without claiming a causal or cultural country effect.

## Questions we should be ready to answer

- Why five countries? They are the five largest groups; all smaller groups remain in supporting tables.
- Why January–April 2023? It is a common calendar restriction based on observed date support,
  before India's May endpoint; it was not selected to maximize an interaction contrast.
- How are sparse cells handled? We retain zero and small counts, mark `n < 10`, and do not
  impute missing strata or silently renormalize weights. This marker is not an inference threshold.
- Are the two weighting checks a joint adjustment? No. Platform mix and before/after-2023
  mix are separate descriptive sensitivities; neither removes all composition differences.
- Is a sentiment comparison complete? No. Human-reviewed labels and exclusion decisions are still required.
- Has Liwen approved this? No. Calculations are checked, but teammate review and final team approval remain pending.
