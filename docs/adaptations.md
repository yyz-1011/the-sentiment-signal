# Repository adaptations

The original Group Project files were left in place. The main repository selects the shared cleaned data, latest reports and latest themed presentation. Earlier substantive initial-analysis and Weeks 1–3 work is retained in archive/. Redundant ZIP handoffs, source copies of the same EDA figures, Office lock files, OS files, and older slide editions were omitted.

Notebook copies locate the repository root without private laptop paths, use the canonical cleaned CSV, and direct new files to generated/. Outputs were cleared before execution and refreshed for GitHub reading. Feature exploration is separated from Yuwei’s appended EDA cells. The latter explicitly sets boxplot whiskers to the observed range, matching the caption; Matplotlib’s default uses a 1.5-IQR rule. Original supplied PNG figures are unchanged.

Kelly’s copy fixes the ten selected sentiment labels to match the supplied figure under a frequency tie, prints the subset denominators, changes the y-axis description, and replaces unsupported significance/causal and generalized platform claims with descriptive findings. Main notebooks are in notebooks/; companion copies beside the deck keep its relative notebook links valid.

The reusable cleaning source has portable defaults. The original EDA source has its narrative median formatting corrected to retain fractional values. Archived notebooks and reports are historical snapshots and may retain obsolete execution instructions or draft interpretations. The current README, findings and notebooks are the judge-facing interpretation.

No new general license is assigned to team-authored work. Dataset CC0 metadata is preserved separately. Background artwork and its generation prompts are retained in presentation/theme_assets. The validation report identifies which checks were actually run.
