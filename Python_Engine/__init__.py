#
# This file is part of the Buildings and Habitats object Model (BHoM)
# Copyright (c) 2015 - 2020, the respective contributors. All rights reserved.
#
# Each contributor holds copyright over their respective contributions.
# The project versioning (Git) records all such contribution source information.
#
#
# The BHoM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3.0 of the License, or
# (at your option) any later version.
#
# The BHoM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.
#


import sys
import os
import clr
from glob import glob


bhom_home = os.path.join(os.getenv("ALLUSERSPROFILE"), "BHoM", "Assemblies")
sys.path.append(bhom_home)

# add oM libraries
for assembly in glob(bhom_home + "/*_oM.dll"):
	clr.AddReference(os.path.join(bhom_home, assembly))

# add Engine libraries
for assembly in glob(bhom_home + "/*_Engine.dll"):
	clr.AddReference(os.path.join(bhom_home, assembly))

# add Engine libraries
for assembly in glob(bhom_home + "/*_Adapter.dll"):
	clr.AddReference(os.path.join(bhom_home, assembly))


from System import *
from System.Collections.Generic import *
