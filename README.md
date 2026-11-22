# ComplyBench

**A benchmark for regulation-constrained workflow generation by LLM agents.**

ComplyBench measures whether generated emergency-response workflows actually satisfy
regulatory requirements — not just whether they read fluently. It accompanies the
manuscript *An Ontology-Based Digital Twin Framework for Adaptive Campus Emergency
Response* (under review at *Virtual Reality & Intelligent Hardware*, JCR Q1, IF 6.1)
and can benchmark any planner, from prompt-only LLM generation to ontology-guided
pipelines such as [RegTwin](https://github.com/emptyqing-bit/regtwin).

## Metrics

| Metric | Meaning |
| --- | --- |
| **Coverage** | Share of required tasks present in the generated plan |
| **Full constraint compliance** | Case passes only with 100% coverage and zero violations |
| **Structural quality** | Share of generated tasks with valid roles, deadlines and approval flags |
| **Violations** | Invalid roles, out-of-range deadlines, missing approval flags |

## Quick start

Python 3.10+, no third-party dependencies.

```bash
python examples/run_benchmark.py       # offline: oracle / ablation / random baselines
python -m unittest discover tests     # 5 unit tests
```

Sample output:

| Runner | Cases | Mean coverage | Full compliance | Structural quality | Violations |
| --- | --- | --- | --- | --- | --- |
| oracle | 4 | 100.00% | 100.00% | 100.0 | 0 |
| partial-ablation | 4 | 68.75% | 0.00% | 54.2 | 4 |
| random-subset | 4 | 54.17% | 0.00% | 25.0 | 6 |

## Benchmarking a real LLM

```python
from complybench import LLMRunner, load_cases, run_benchmark, markdown_report

cases = load_cases("data/sample_cases.json")
naive = LLMRunner("http://localhost:11434", "qwen2.5", guided=False)  # any OpenAI-compatible endpoint
guided = LLMRunner("http://localhost:11434", "qwen2.5", guided=True)   # adds roles + constraints to the prompt
print(markdown_report(run_benchmark(cases, [naive, guided])))
```

The guided vs naive comparison isolates the effect of constraint grounding —
the central research question of the accompanying manuscript.

## Repository layout

| Path | Contents |
| --- | --- |
| `complybench/cases.py` | Case schema and loader |
| `complybench/runners.py` | Oracle / ablation / random baselines + LLM runner (naive & guided) |
| `complybench/evaluate.py` | Coverage, compliance, structural quality, aggregation |
| `complybench/report.py` | Benchmark driver and Markdown report |
| `data/sample_cases.json` | Four synthetic sample cases (schema reference) |

## Dataset

The full 850-case set used in the manuscript is not redistributed here. The bundled
cases are **synthetic samples** documenting the schema; open an issue to request
academic access to the full set.

## License

MIT — see [LICENSE](LICENSE).
