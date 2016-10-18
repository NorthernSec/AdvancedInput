import subprocess
import difflib
import AdvancedInput

def bashcomplete(buffer = None, **kwargs):
  def _files(buff=""):
    _c = "compgen -o default %s"%buff
    return subprocess.Popen(_c, shell=True, executable="/bin/bash",
                            stdout=subprocess.PIPE).stdout.read().decode('utf-8')[:-1]
  def _commands(buff=""):
    _c = "compgen -A command | grep ^%s"%buff
    return subprocess.Popen(_c, shell=True, executable="/bin/bash",
                            stdout=subprocess.PIPE).stdout.read().decode('utf-8')[:-1]

  match = buffer.split(" ")[-1]
  results = _commands(match)
  parts = buffer.split(" ")
  if not results:
    results = _files(match)
  if not results: return         # Nothing changed
  elif results.count("\n") == 0: # 1 match
    parts[-1] = results
    return {'buffer': " ".join(parts)+" "}
  else:                          # Multiple posibilities
    _to_diff = results.split("\n")
    same=_to_diff.pop(0)         # -> calculate shortest same
    for i in _to_diff:
      _diff = ''.join([x[0] for x in (difflib.ndiff(same, i))])
      same = same[:(min(_diff.index('+'), _diff.index('-')))]
    if same == match: # Can't expand the line, ask to return options
      text="Display all %s posibilities?"%(results.count('\n')+1)
      if results.count('\n') < 15 or AdvancedInput.confirm(text):
        print();print(results)
    else:
      parts = buffer.split(" ")
      parts[-1] = same
      return {'buffer': " ".join(parts)}
