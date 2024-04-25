import time
import pandas as pd
import re
from collections import deque
from itertools import product
from functools import reduce


templateQueries = [
    
    "SELECT * from inventory",
         
    "SELECT * from inventory where {column:int64} > [value:int64]",
    "SELECT * from inventory where {column:int64} > [value:int64]",
    "SELECT * from inventory where {column:int64} < [value:int64]",
    "SELECT * from inventory where {column:int64} = [value:int64]",
    "SELECT * from inventory where {column:int64} != [value:int64]",
    "SELECT * from inventory where {column:int64} >= [value:int64]",
    "SELECT * from inventory where {column:int64} <= [value:int64]",
    
    "SELECT {column:object} from inventory where {column:int64} > [value:int64]",
    "SELECT {column:object} from inventory where {column:int64} < [value:int64]",
    "SELECT {column:object} from inventory where {column:int64} = [value:int64]",
    "SELECT {column:object} from inventory where {column:int64} != [value:int64]",
    "SELECT {column:object} from inventory where {column:int64} >= [value:int64]",
    "SELECT {column:object} from inventory where {column:int64} <= [value:int64]",
    
    "SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64]",
    "SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64]",
    "SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64]",
    "SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64]",
    "SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64]",
    "SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64]",
    
    "SELECT * from inventory where {column:object} = [value:object]",
    "SELECT * from inventory where {column:object}!= [value:object]",
    
    "SELECT {column:object} where {column:object} = [value:object]",
    "SELECT {column:object} where {column:object} != [value:object]", 
    
    "SELECT {column:object},{column:int64} where {column:object} = [value:object]",
    "SELECT {column:object},{column:int64} where {column:object} != [value:object]",
    
      'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} > [value:int64] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} > [value:int64] or {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} < [value:int64] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} < [value:int64] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} < [value:int64] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} < [value:int64] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} < [value:int64] or {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} = [value:int64] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} = [value:int64] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} = [value:int64] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} = [value:int64] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} = [value:int64] or {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} != [value:int64] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} != [value:int64] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} != [value:int64] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} != [value:int64] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} != [value:int64] or {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} >= [value:int64] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} >= [value:int64] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} >= [value:int64] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} >= [value:int64] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} >= [value:int64] or {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} <= [value:int64] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:int64} <= [value:int64] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} <= [value:int64] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:int64} <= [value:int64] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:int64} <= [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} > [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} < [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} = [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} != [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} >= [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object} from inventory where {column:int64} <= [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} > [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} < [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} = [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} != [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} >= [value:int64] or {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] and {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] and {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] and {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] and {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] and {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] and {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] or {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] or {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] or {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] or {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] or {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] or {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] and {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] and {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] or {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} from inventory where {column:int64} <= [value:int64] or {column:object} != [value:object]',
     'SELECT * from inventory where {column:object} = [value:object] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:object} = [value:object] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:object} = [value:object] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:object} = [value:object] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:object} = [value:object] or {column:object} != [value:object]',
     'SELECT * from inventory where {column:object}!= [value:object] and {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] and {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] and {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] and {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] and {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] and {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] or {column:int64} > [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] or {column:int64} = [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] or {column:int64} < [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] or {column:int64} != [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] or {column:int64} >= [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] or {column:int64} <= [value:int64]',
     'SELECT * from inventory where {column:object}!= [value:object] and {column:object} = [value:object]',
     'SELECT * from inventory where {column:object}!= [value:object] and {column:object} != [value:object]',
     'SELECT * from inventory where {column:object}!= [value:object] or {column:object} = [value:object]',
     'SELECT * from inventory where {column:object}!= [value:object] or {column:object} != [value:object]',
     'SELECT {column:object} where {column:object} = [value:object] and {column:int64} > [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] and {column:int64} = [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] and {column:int64} < [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] and {column:int64} != [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] and {column:int64} >= [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] and {column:int64} <= [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] or {column:int64} > [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] or {column:int64} = [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] or {column:int64} < [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] or {column:int64} != [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] or {column:int64} >= [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] or {column:int64} <= [value:int64]',
     'SELECT {column:object} where {column:object} = [value:object] and {column:object} = [value:object]',
     'SELECT {column:object} where {column:object} = [value:object] and {column:object} != [value:object]',
     'SELECT {column:object} where {column:object} = [value:object] or {column:object} = [value:object]',
     'SELECT {column:object} where {column:object} = [value:object] or {column:object} != [value:object]',
     'SELECT {column:object} where {column:object} != [value:object] and {column:int64} > [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] and {column:int64} = [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] and {column:int64} < [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] and {column:int64} != [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] and {column:int64} >= [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] and {column:int64} <= [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] or {column:int64} > [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] or {column:int64} = [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] or {column:int64} < [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] or {column:int64} != [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] or {column:int64} >= [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] or {column:int64} <= [value:int64]',
     'SELECT {column:object} where {column:object} != [value:object] and {column:object} = [value:object]',
     'SELECT {column:object} where {column:object} != [value:object] and {column:object} != [value:object]',
     'SELECT {column:object} where {column:object} != [value:object] or {column:object} = [value:object]',
     'SELECT {column:object} where {column:object} != [value:object] or {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] and {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] and {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] and {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] and {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] and {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] and {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] or {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] or {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] or {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] or {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] or {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] or {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] and {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] and {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] or {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} where {column:object} = [value:object] or {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] and {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] and {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] and {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] and {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] and {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] and {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] or {column:int64} > [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] or {column:int64} = [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] or {column:int64} < [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] or {column:int64} != [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] or {column:int64} >= [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] or {column:int64} <= [value:int64]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] and {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] and {column:object} != [value:object]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] or {column:object} = [value:object]',
     'SELECT {column:object},{column:int64} where {column:object} != [value:object] or {column:object} != [value:object]'
]

def getClassificationDict(df):
    columnDatatypeDict = df.dtypes.astype(str).to_dict()
    columnClassificationDict = {}
    for key, value in columnDatatypeDict.items():
        if value in columnClassificationDict:
            columnClassificationDict[value].append(key)
        else:
            columnClassificationDict[value] = [key]
    return columnClassificationDict
  
def getTokenValueAndDatatype(text):
    match = re.search(r"\{(.*?)\}", text)
    if match:
        token = match.group(1)
        return token.split(':')
    else:
        return None, None
      
def formatQuery(query, df):
    columnClassificationDict = getClassificationDict(df)
    tokenPattern = r'\{[^}]*\}'  # Matches any substring enclosed in {}
    queue = deque()
    result = []
    queue.append(query)
    while len(queue) > 0:
        frontQuery = queue[0]
        queue.popleft()
        match = re.search(tokenPattern, frontQuery)
        if match:
            firstToken = match.group(0)
            tokenValue, tokenDatatype = getTokenValueAndDatatype(firstToken)
            if tokenValue == 'column':
                for column in columnClassificationDict[tokenDatatype]:
                    tempQuery = re.sub(tokenPattern, column, frontQuery, count=1)
                    queue.append(tempQuery)
        else:
            result.append(frontQuery)
    return result
  
def generateQueries(queries, df):
    queryDict = {}
    for query in queries:
        queryDict[query] = formatQuery(query, df)
    return queryDict

def transform(id, string, tokens):
    replacement_lists = [tokens.get(key, [key]) for key in string.split()]
    permutations = product(*replacement_lists)
    temp = [' '.join(permutation) for permutation in permutations]
    return [(id,i) for i in temp]

files = ['inventory.csv','students.csv','bugReport.csv']
q_range = [26,101,len(templateQueries)]


tokens = {
    'inventory.csv': [
        {
            "SELECT": ["Give me"],
            "*": ["all values"],
            "FROM": ["from"],
            "inventory": ["inventory table"],
            "unit Price": ["unit price"],
            "quantityInStock": ["quantity in stock"],
            "productID": ["product id"],
            "=": ["is equal to"],
            "!=": ["is not equal to"],
            " > ": ["is greater than "],
            " < ": ["is less than "]
        },
        {
            "SELECT": ["Give me", "I want", "Show me", ""],
            "*": ["all values", "all results"],
            "FROM": ["belonging to", "inside", "from", "in"],
            "unit Price": ["unit price"],
            "inventory": ["inventory table"],
            "quantityInStock": ["quantity in stock","quantity","stock"],
            "productID": ["product id"],
            "=": [" is equal to ", " equals ", " is same as ", "="],
            "!=": [" is not equal to ", " not equals ", " not same as ", "!="],
            " > ": [" is greater than ", " is more than ", " is higher than ", " > "],
            " < ": [" is lesser than ", " is less than ", " is lower than ", " < "]
        }
    ],
    'students.csv': [
        {
            "SELECT": ["Give me"],
            "*": ["all values"],
            "FROM": ["from"],
            "gpa": ["grade"],
            "studentName": ["name"],
            "studentId": ["student id"],
            "=": ["is equal to"],
            "!=": ["is not equal to"],
            " > ": ["is greater than "],
            " < ": ["is less than "]
        },
        {
            "SELECT": ["Give me", "I want", "Show me", ""],
            "*": ["all values", "all results"],
            "FROM": ["belonging to", "inside", "from", "in"],
            "gpa": ["grade", "GPA"],
            "studentName": ["name", "student name"],
            "division": ["division","section"],
            "studentId": ["student id", "id"],
            "=": [" is equal to ", " equals ", " is same as ", "="],
            "!=": [" is not equal to ", " not equals ", " not same as ", "!="],
            " > ": [" is greater than ", " is more than ", " is higher than ", " > "],
            " < ": [" is lesser than ", " is less than ", " is lower than ", " < "]
        }
    ],
    'bugReport.csv': [
        {
            "SELECT": ["Give me"],
            "*": ["all values"],
            "FROM": ["from"],
            "detectedBy": ["detected by"],
            "assignedTo": ["is assigned to"],
            "bugId": ["bug id"],
            "=": ["is equal to"],
            "!=": ["is not equal to"],
            " > ": ["is greater than "],
            " < ": ["is less than "]
        },
        {
            "SELECT": ["Give me", "I want", "Show me", ""],
            "*": ["all values", "all results"],
            "FROM": ["belonging to", "inside", "from", "in"],
            "detected": ["is detected by", "is found by"],
            "assignedTo": ["is assigned to"],
            "bugId": ["bug id"],
            "=": [" is equal to ", " equals ", " is same as ", "="],
            "!=": [" is not equal to ", " not equals ", " not same as ", "!="],
            " > ": [" is greater than ", " is more than ", " is higher than ", " > "],
            " < ": [" is lesser than ", " is less than ", " is lower than ", " < "]
        }        
    ]
    
}


steps = 1000

for f in files:
    # 3 files
    inter_state = []
    df = pd.read_csv(f)
    avg_time = 0
    print("="*30,"file:",f," length:",len(df),"="*30)
    for j in q_range:
        # 3 template ranges
        for i in range(steps):
            # repeat i times for unbaised avg        
            start_time = time.time()
            queryDict = generateQueries(templateQueries[:j], df)
            execution_time = time.time() - start_time
            avg_time += execution_time*1000
        lst = []
        for q in queryDict.values():
            lst += q
        print("template_length:",j,"generated templates:",len(lst)," time:","{:.2f}".format(avg_time/steps))
        for token in tokens[f]:
            for i in range(steps):
                start_time = time.time()
                for idx, query in enumerate(lst):
                    inter_state += transform(idx,query,token)
                execution_time = time.time() - start_time
                avg_time += execution_time*1000
            print("token_subs:",reduce(lambda x, y: x * len(token[y]), token, 1),"generated IMF:",len(inter_state)," time:","{:.2f}".format(avg_time/steps))
        print("")
        
        