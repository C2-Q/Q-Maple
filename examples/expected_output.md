# Expected Output

Running `python -m qmaple.demo` should print a short summary and write `outputs/sample_result.json`.

For the committed example data, the intended recommendations are:

- `r1_compute` -> `SC`
- `r2_feedback` -> `SC`
- `r3_scale` -> `NA`

The exact score values are part of the JSON output. The main expectation is that each region receives a ranked candidate list and a short plain-language reason for the top choice.
