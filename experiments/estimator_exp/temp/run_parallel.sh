cores=$(fgrep -c processor /proc/cpuinfo)
xargs --arg-file=run_all.sh \
      --max-procs=$cores  \
      --replace \
      --verbose \
      /bin/sh -c "{}"

