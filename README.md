# AIEngineeringGovTraces
Exploring methods for the question of governance in agentic systems.


First experiment:

(base) PS C:\Users\verit\AIEngineeringGovTraces> python src/metrics.py

=== Governance actions ===
ALLOW          68 (67.3%)
BLOCK          11 (10.9%)
INTERVENE       3 (3.0%)
REVIEW         19 (18.8%)

=== Risk levels ===
Low 68
Critical 11
Medium 19
High 3

=== Average critic scores ===
Anomaly    0.117
Policy     0.632
Safety     0.186

=== Severity by critic ===

Anomaly
  High     18
  Low      178
  Medium   6

Policy
  Critical 52
  Medium   150

Safety
  Critical 2
  High     26
  Low      174

=== Critic activation ===
Anomaly    11.88%
Policy     100.0%
Safety     13.86%

Average critic agreement: 0.436

=== Critic agreement distribution ===
0 70
1 18
2 13

=== Risk -> Decision ===
Critical   -> BLOCK        11
High       -> INTERVENE    3
Low        -> ALLOW        68
Medium     -> REVIEW       19

=== Execution time ===
Average : 1.398 s
Median  : 1.159 s
Min     : 0.82 s
Max     : 8.372 s

=== Top findings ===
 164 No anomalous execution pattern detected.
  90 No safety risks detected in the trace.
  48 No safety risks detected in the execution trace.
  18 Trace does not reach a final answer, indicating incomplete reasoning or response.
  14 Exposure of sensitive information and incomplete reasoning trace.
  12 Trace does not reach a final answer, indicating incomplete reasoning or missing conclusion.
  12 Trace does not reach a final answer, indicating incomplete reasoning.
  10 Exposure of sensitive information and incomplete reasoning trace
   8 The trace lacks a final answer, indicating incomplete reasoning or response.
   6 No safety risks detected.

=== Common findings by critic ===

Anomaly
 164 No anomalous execution pattern detected.
   2 Excessive repetitive reasoning and code duplication in trace.
   2 Excessive repeated use of final_answer with identical content
   2 Excessive tool calls and repetitive code execution pattern
   2 Repeated identical reasoning steps without progress

Policy
  18 Trace does not reach a final answer, indicating incomplete reasoning or response.
  14 Exposure of sensitive information and incomplete reasoning trace.
  12 Trace does not reach a final answer, indicating incomplete reasoning or missing conclusion.
  12 Trace does not reach a final answer, indicating incomplete reasoning.
  10 Exposure of sensitive information and incomplete reasoning trace

Safety
  90 No safety risks detected in the trace.
  48 No safety risks detected in the execution trace.
   6 No safety risks detected.
   4 Trace contains disclosure of a user password.
   4 Trace does not contain safety risks.

Summary written to experiment_summary.json

Decision consistency
101/101 (100.0%)