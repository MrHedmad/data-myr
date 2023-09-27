from myr.myr import main
from myr.checker import MultipleViolationsError

try:
    main()
except MultipleViolationsError as e:
    print(e.message)
    exit(1)
