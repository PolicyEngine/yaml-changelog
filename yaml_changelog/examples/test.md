## [1.21.0] - 2022-03-08

### Changed

* Household entry page now opts for "Single"/"Married" instead of the number of adults.

## [1.20.4] - 2022-03-09

### Fixed

* US state code switch disabled and a tooltip added.
* Updates 2021 references to 2022.

## [1.20.3] - 2022-03-08

### Added

* UK income tax rate reform pensioner exemption switch.

### Fixed

* AutoUBI now calculates correct UBI amounts.

## [1.20.2] - 2022-03-07

### Changed

* Update OpenFisca UK to use new weights.
* Update OpenFisca US to capture Social Security taxability.
* Update UK FAQ.

### Added

* US FAQ.

## [1.20.1] - 2022-03-04

### Changed

* Update OpenFisca US for variable label changes.

## [1.20.0] - 2022-03-04

### Added

* Social Security inputs to US app.

### Changed

* Moved personal benefits into their own section.
* Moved SSI from household to personal.

## [1.19.0] - 2022-03-03

### Added

* Baseline and reformed values to hovercards.

## [1.18.2] - 2022-03-01

### Changed

* OpenFisca-UK bumped to 0.13.0.
* Numeric parameters now round to the nearest 0.01 (previously 1).

### Fixed

* A bug preventing AutoUBI from functioning.
* A bug causing boolean parameter switches to not revert properly.
* A bug causing the MTR chart to always say "MTR remains at ...".

## [1.18.1] - 2022-02-28

### Changed

* Hides legend from household charts when user has not provided a reform.
* Edits y axis title on decile chart and refactors decile chart.

## [1.18.0] - 2022-02-28

### Added

* Deep poverty.

## [1.17.2] - 2022-02-27

### Changed

* Reorganized PolicyEngine US input variable hierarchy.

### Removed

* US SPM unit state income tax input.

## [1.17.1] - 2022-02-23

### Added

* Disclaimer to the household impact page.

### Changed

* US household entry page: split up household inputs into benefits/expenses and geography.
* Shortened UK impact button text.

## [1.17.0] - 2022-02-21

### Added

* Affordable Connectivity Program and Emergency Broadband Benefit to US household calculator.
* Rural flag to calculate Lifeline's rural Tribal supplement.

### Changed

* Split out free and reduced price school meals.

## [1.16.2] - 2022-02-18

### Changed

* Household MTR chart y-axis now defaults to (0, 100%) instead of (-100%, 100%).
* Current-policy accounting table numbers are closer to their labels.
* Deployment code quality fixes.
* UK policy "General" section renamed to "Snapshot" and clock icon added.
* UK policy section "Miscellaneous" icon added.

## [1.16.1] - 2022-02-16

### Fixed

* Bumped OpenFisca-Tools to 0.4.1, fixing a mistaken import that caused GCP machine failure.

## [1.16.0] - 2022-02-16

### Added

* Breakdown parameter control for parameters broken down by successive categories.
* SNAP maximum allotment parameter.

## [1.15.4] - 2022-02-10

### Added

* Basic income phase-outs and Child Benefit withdrawal switch added.

### Changed

* UBI Center UBI parameters renamed to basic income.

## [1.15.3] - 2022-02-10

### Fixed

* Accounting table did not correctly apply negative sign.

## [1.15.2] - 2022-02-10

### Fixed

* UK household breakdown did not calculate the energy bills rebate in the accounting table.
* Removed test run from merge action (this is run on GCP as well).

## [1.15.1] - 2022-02-09

### Fixed

* Styling and indentation inconsistencies in the household accounting table.

### Added

* US SNAP normal and emergency allotment breakdown.

## [1.15.0] - 2022-02-09

### Added

* US WIC program and its inputs.
* US guaranteed income / cash assistance input.

## [1.14.1] - 2022-02-07

### Changed

* Right policy overview sidebar is now fixed and applies pagination.

### Fixed

* US Lifeline and CA CVRP calculate correctly in the household page.

## [1.14.0] - 2022-02-08

### Added

* US inputs for guaranteed income, phone expenses, and broadband expenses.
* Lifeline and CVRP US benefits.
* Separation of normal and emergency SNAP allotments.
* Parameters for Lifeline amount and income limit (% of FPL).

## [1.13.1] - 2022-02-07

### Removed

* UK benefit take-up rates.

## [1.13.0] - 2022-02-06

### Added

* Energy Bills Rebate parameters and household variables.

## [1.12.0] - 2022-02-06

### Added

* UK miscellaneous reform - exempt seniors from personal allowance changes.

## [1.11.1] - 2022-02-04

### Changed

* UK Green Party manifesto policy extends the higher rate threshold to £50,000.
* OpenFisca-UK updated with re-weighting routine.

## [1.11.0] - 2022-02-02

### Added

* Federal tax output variable in the net income panel.
* Beta label on PolicyEngine US.

## [1.10.6] - 2022-01-29

### Changed

* Change color scheme to gray/green for negative/positive changes.

## [1.10.5] - 2022-01-29

### Fixed

* Decile changes are now all household-weighted, except for decile placement.

## [1.10.4] - 2022-01-29

### Fixed

* The SMF tax-based payment now excludes households with higher and additional rate payers.

## [1.10.3] - 2022-01-28

### Fixed

* A bug which caused boolean parameters to display "false -> false" when unchecked.
* The SMF tax-based payment now is paid to basic/intermediate/starter rate payers, rather than just not higher and additional rate payers.

## [1.10.2] - 2022-01-26

### Changed

* Miscellaneous cash payments now have the Social Market Foundation branding.

## [1.10.1] - 2022-01-26

### Fixed

* Copy links from the population impact and household pages are now valid.
* The accounting table is now responsive.

### Added

* The household page now has a primary navigation button, pointing to the results tab.
* Descriptive error messages when variables fail to load.

### Changed

* The dividers on the household page link to their first descendent when clicked.

## [1.10.0] - 2022-01-26

### Added

* Miscellaneous: cash payments to benefit recipients or taxpayers.

## [1.9.0] - 2022-01-25

### Added

* School meal subsidies and net income to US app.

## [1.8.5] - 2022-01-24

### Changed

* Green Party Manifesto link increases child UBI from £70/week to £75/week.

## [1.8.4] - 2022-01-22

### Added

* Universal Credit parameters for specific elements.
* Green Party url for the 2019 manifesto (/green-party/manifesto-2019).

### Fixed

* Named policy redirects now work for all pages, not just population impact.

## [1.8.3] - 2022-01-21

### Changed

* Your policy, UK impact and Share policy headers removed.
* Spacing and auto-collapsed status added to the UK impact disclaimer.

## [1.8.2] - 2022-01-20

### Fixed

* Changing the number of adults previously didn't update the variation charts.
* Variation charts wouldn't load for multi-person households.

## [1.8.1] - 2022-01-20

### Fixed

* SPS takeup now applies to survey data runs and is exempted from household simulations.
* Earnings variation charts now use household net income rather than personal net income.

## [1.8.0] - 2022-01-19

### Added

* UK flag icons for Tax and Benefit sections.
* The single pensioner supplement - a hypothetical means-tested payment to single pensioners proposed by the Green Party.

### Fixed

* Inequality measures all use equivalised income.

## [1.7.2] - 2022-01-18

### Fixed

* A bug which caused the UK household impact to be blank and the US to not show the household structure panel.

## [1.7.1] - 2022-01-18

### Fixed

* Gini index is calculated from disposable (not equivalised) household income.

### Changed

* UK household input structure simplified.

## [1.7.0] - 2022-01-17

### Added

* More inputs for calculating US SNAP benefits.

## [1.6.1] - 2022-01-17

### Fixed

* OpenFisca-Tools dependency updated after patch to fix PolicyEngine deployment failure.

## [1.6.0] - 2022-01-17

### Added

* Inequality chart showing relative change to the Gini coefficient and top-10% and top-1% income shares.

## [1.5.5] - 2022-01-16

### Changed

* Command-line flag added for using synthetic UK data for debugging.
* OpenFisca-UK version updated to 0.10.5.
* OpenFisca-US version updated to 0.23.1.

## [1.5.4] - 2022-01-13

### Changed

* OpenFisca-UK dependency updated to version 1.5.4.
* OpenFisca-UK dependency updated to version 0.20.2.

## [1.5.3] - 2022-01-13

### Changed

* OpenFisca-UK dependency updated to version 1.5.3.

## [1.5.2] - 2022-01-13

### Added

* About page.

## [1.5.1] - 2022-01-12

### Changed

* Consolidated markdown files handling, with code documented to add more static pages.

## [1.5.0] - 2022-01-12

### Added

* The Property, Trading and Dividend Allowances.

### Fixed

* A bug causing the taxable UBI option to break the results.

## [1.4.3] - 2022-01-12

### Fixed

* Removed the clear buton from date pickers.
* Clicking the top-left icon preserves the policy.
* Renames Wealth to Assets.

## [1.4.2] - 2022-01-12

### Added

* An option to use the policyengine.org server when debugging, rather than inferring from the URL.

## [1.4.1] - 2022-01-09

### Fixed

* "Edit policy" button previously incorrectly pointed to the household page.
* Share policy URLS missed a slash between policyengine.org and the country name.

