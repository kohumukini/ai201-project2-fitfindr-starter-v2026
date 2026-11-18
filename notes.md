== results/gunicorn.jsonl [3-burst]: 3 requests ==
full runs 3, stopped early (200 + error) 0, non-200 0
full-run duration: mean 4.49s  median 3.21s  max 7.14s
  parse_query      mean 1.04s
  search_listings  mean 0.32s
  suggest_outfit   mean 2.21s
  create_fit_card  mean 0.92s
tokens per full run: prompt 992, output 268
model calls per full run: 3.0

== results/gunicorn.jsonl [10-burst]: 10 requests ==
full runs 10, stopped early (200 + error) 0, non-200 0
full-run duration: mean 12.12s  median 3.62s  max 46.96s
  parse_query      mean 0.95s
  search_listings  mean 0.31s
  suggest_outfit   mean 8.96s
  create_fit_card  mean 1.89s
tokens per full run: prompt 999, output 278
model calls per full run: 3.1

