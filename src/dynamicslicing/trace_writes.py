# Implement a DynaPyt analysis to trace all writes by printing them to stdout.
from typing import Any, List, Callable, Optional
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TraceWritesAnalysis(BaseAnalysis):
    def write(self, dyn_ast: str, iid: int, old_vals: List[Callable], new_val: Any) -> Any:
        print(new_val)      # print the value each time a variable is being written to
