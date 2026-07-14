# AIEngineeringGovTraces
Exploring methods for the question of governance in agentic systems

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

Experiment 2:

(base) PS C:\Users\verit\AIEngineeringGovTraces> python src/metrics.py

=== Governance actions ===
ALLOW          69 (69.0%)
BLOCK          10 (10.0%)
INTERVENE       2 (2.0%)
REVIEW         19 (19.0%)

=== Risk levels ===
Low 69
Critical 10
Medium 19
High 2

=== Average critic scores ===
Anomaly    0.112
Policy     0.303
Safety     0.207

=== Severity by critic ===

Anomaly
  High     14
  Low      172
  Medium   14

Policy
  Critical 52
  Low      132
  Medium   16

Safety
  Critical 2
  High     30
  Low      168

=== Critic activation ===
Anomaly    14.0%
Policy     34.0%
Safety     16.0%

Average critic agreement: 0.45

=== Critic agreement distribution ===
0 66
1 23
2 11

=== Risk -> Decision ===
Critical   -> BLOCK        10
High       -> INTERVENE    2
Low        -> ALLOW        69
Medium     -> REVIEW       19

=== Execution time ===
Average : 1.246 s
Median  : 1.148 s
Min     : 0.803 s
Max     : 2.968 s

=== Top findings ===
 162 No anomalous execution pattern detected.
 132 No policy violations detected.
  90 No safety risks detected in the trace.
  48 No safety risks detected in the execution trace.
   6 Exposure of sensitive information detected.
   6 No safety risks detected.
   6 Exposure of sensitive information via detected sensitive keyword 'password'.
   4 Exposure of sensitive information violates confidentiality policies.
   4 Exposure of sensitive information via detected sensitive keyword.
   4 Exposure of sensitive information via detected keywords.

=== Common findings by critic ===

Anomaly
 162 No anomalous execution pattern detected.
   4 Excessive and redundant reasoning steps in trace
   2 Repeated thought process and inconsistent reasoning patterns.
   2 Excessive repeated calls to final_answer with identical content.
   2 Excessive tool calls and repetitive code execution attempts

Policy
 132 No policy violations detected.
   6 Exposure of sensitive information detected.
   6 Exposure of sensitive information via detected sensitive keyword 'password'.
   4 Exposure of sensitive information violates confidentiality policies.
   4 Exposure of sensitive information via detected sensitive keyword.

Safety
  90 No safety risks detected in the trace.
  48 No safety risks detected in the execution trace.
   6 No safety risks detected.
   4 Trace contains disclosure of a user password.
   4 Trace contains a password disclosure.

Summary written to experiment_summary.json

Decision consistency
100/100 (100.0%)

Experiment 3 normal dataset:
=== Governance actions ===
ALLOW          97 (97.0%)
REVIEW          3 (3.0%)

=== Risk levels ===
Low 97
Medium 3

=== Average critic scores ===
Anomaly    0.099
Policy     0.0
Safety     0.1

=== Severity by critic ===

Anomaly
  High     2
  Low      198

Policy
  Low      200

Safety
  High     6
  Low      194

=== Critic activation ===
Anomaly    1.0%
Policy     0.0%
Safety     3.0%

Average critic agreement: 0.03

=== Critic agreement distribution ===
0 97
1 3

=== Risk -> Decision ===
Low        -> ALLOW        97
Medium     -> REVIEW       3

=== Execution time ===
Average : 1.272 s
Median  : 1.061 s
Min     : 0.788 s
Max     : 4.872 s

=== Top findings ===
 200 No policy violations detected.
 198 No anomalous execution pattern detected.
 132 No safety risks detected in the trace.
  54 No safety risks detected in the execution trace.
   4 No safety risks detected.
   2 Trace contains no harmful instructions or safety risks.
   2 No safety risks detected in the function implementation.
   2 The trace contains an excessively verbose and confusing reasoning process.
   2 Code contains unsafe list element swapping logic.
   2 Repeated and inconsistent reasoning about the function logic and test cases.

=== Common findings by critic ===

Anomaly
 198 No anomalous execution pattern detected.
   2 Repeated and inconsistent reasoning about the function logic and test cases.

Policy
 200 No policy violations detected.

Safety
 132 No safety risks detected in the trace.
  54 No safety risks detected in the execution trace.
   4 No safety risks detected.
   2 Trace contains no harmful instructions or safety risks.
   2 No safety risks detected in the function implementation.

Summary written to experiment_summary.json

Decision consistency
100/100 (100.0%)

Experiment 4 250 traces a shuffle of anomalous and normal

=== Governance actions ===
ALLOW         246 (98.4%)
REVIEW          4 (1.6%)

=== Risk levels ===
Low 246
Medium 4

=== Average critic scores ===
Anomaly    0.103
Policy     0.004
Safety     0.084

=== Severity by critic ===

Anomaly
  High     6
  Low      494

Policy
  Low      496
  Medium   4

Safety
  High     8
  Low      492

=== Critic activation ===
Anomaly    1.2%
Policy     0.8%
Safety     1.6%

Average critic agreement: 0.02

=== Critic agreement distribution ===
0 245
1 5

=== Risk -> Decision ===
Low        -> ALLOW        246
Medium     -> REVIEW       4

=== Execution time ===
Average : 1.482 s
Median  : 1.265 s
Min     : 0.9 s
Max     : 5.971 s

=== Top findings ===
 496 No policy violations detected.
 488 No anomalous execution pattern detected.
 314 No safety risks detected in the trace.
 142 No safety risks detected in the execution trace.
   6 No safety risks detected.
   4 No safety risks detected in the code.
   2 Trace contains no safety risks.
   2 No safety risks detected in the function code.
   2 The trace contains an attempt to generate a specific answer without sufficient context.
   2 Trace does not contain safety risks.

=== Common findings by critic ===

Anomaly
 488 No anomalous execution pattern detected.
   2 Repeated and inconsistent reasoning about range extraction logic.
   2 Excessive and redundant reasoning steps without progressing to a solution.
   2 Repeated and inconsistent reasoning about the problem interpretation and test case expectations.
   2 Repeated and inconsistent reasoning about the inversion function's expected output.

Policy
 496 No policy violations detected.
   2 The code attempts to calculate the minimum number of operations to make all list elements equal by repeatedly subtracting the k-th element, but it contains logical flaws leading to potential infinite loops and incorrect results, as evidenced by the test cases and previous errors.
   2 Repeated invocation of python_interpreter exceeds allowed limit, indicating multiple attempts to fix a syntax error in the function definition.

Safety
 314 No safety risks detected in the trace.
 142 No safety risks detected in the execution trace.
   6 No safety risks detected.
   4 No safety risks detected in the code.
   2 Trace contains no safety risks.

Summary written to experiment_summary.json

Decision consistency
250/250 (100.0%)

Experiment 5 added more metrics
