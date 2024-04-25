import time
import pandas as pd
import re
from collections import deque
from itertools import product
from functools import reduce
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import os


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

inter_state = []

df = pd.read_csv('inventory.csv')
queryDict = generateQueries(templateQueries, df)
lst = []
for q in queryDict.values():
    lst += q
for idx, query in enumerate(lst):
    inter_state += transform(idx,query,tokens['inventory.csv'][1])


# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load pre-trained model and tokenizer
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)

# Function to encode sentences into embeddings
def encode_sentences(sentences):
    encoded_sentences = []
    for sentence in sentences:
        # Tokenize input text and get model embeddings
        inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        # Extract embeddings from model output
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        encoded_sentences.append(embeddings)
    return np.vstack(encoded_sentences)

def find_top_match(query_sentence):
    # Encode query sentence on CPU
    query_embedding = encode_sentence_on_cpu(query_sentence)
    
    # Search for the top matching vector on CPU
    D, I = index.search(np.expand_dims(query_embedding.numpy(), axis=0), 1)
    
    # Return the top matching vector and distance
    return inter_state[I[0][0]], D[0][0]

def find_top_n_matches(query_sentence, n=5):
    # Encode query sentence on CPU
    query_embedding = encode_sentence_on_cpu(query_sentence)
    
    # Search for the top n matching vectors on CPU
    D, I = index.search(np.expand_dims(query_embedding.numpy(), axis=0), n)
    
    # Return the top n matching vectors and distances
    return [(inter_state[i], d) for d, i in zip(D[0], I[0])]

def encode_sentence_on_cpu(sentence):
    # Tokenize input text and get model embeddings
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Extract embeddings from model output
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return torch.from_numpy(embeddings)

# Assuming index, tokenizer, model, inter_state, and device are defined


import time
for l in [10,100,500,1000,10000,100000]:
    temp = [s for i,s in inter_state[:l]]
    start_time = time.time()
    embeddings = encode_sentences(temp)
    execution_time = time.time() - start_time
    print("time to embed",l," sentences:","{:.2f}".format(execution_time*1000))
    index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance metric
    start_time = time.time()
    index.add(embeddings)
    execution_time = time.time() - start_time
    print("time to index",l," sentences:","{:.2f}".format(execution_time*1000))
    # Find the top match
    query_sentence = [inter_state[0][1],inter_state[10][1],inter_state[100][1],inter_state[1000][1],inter_state[10000][1],inter_state[50000][1]]
    avg1,avg2 = 0,0
    for q in query_sentence:
        start_time = time.time()
        top_match, distance = find_top_match(q)
        execution_time = time.time() - start_time
        avg1+=execution_time

      
    print("time to search",l," sentences:","{:.2f}".format(avg1/6*1000))
    for x in [2,3,4,5]:
            # Find the top 5 matches
        start_time = time.time()
        top_matches = find_top_n_matches(q, n=x)
        execution_time = time.time() - start_time
        avg2+=execution_time
        print("time to",x ,"top search",l," sentences:","{:.2f}".format(avg2/6*1000))

    flat_index = faiss.index_factory(index.d, "Flat")
    flat_index.add(index.reconstruct_n(0, index.ntotal))
    faiss.write_index(flat_index, "index.faiss")
    file_size_bytes = os.path.getsize("index.faiss")
    file_size_mb = file_size_bytes / (1024 * 1024)

    print("Size of pickle file:", file_size_mb, "MB")
    print("")

