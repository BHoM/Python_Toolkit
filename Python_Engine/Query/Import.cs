/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2021, the respective contributors. All rights reserved.
 *
 * Each contributor holds copyright over their respective contributions.
 * The project versioning (Git) records all such contribution source information.
 *                                           
 *                                                                              
 * The BHoM is free software: you can redistribute it and/or modify         
 * it under the terms of the GNU Lesser General Public License as published by  
 * the Free Software Foundation, either version 3.0 of the License, or          
 * (at your option) any later version.                                          
 *                                                                              
 * The BHoM is distributed in the hope that it will be useful,              
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 
 * GNU Lesser General Public License for more details.                          
 *                                                                            
 * You should have received a copy of the GNU Lesser General Public License     
 * along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.      
 */

using Python.Runtime;
using System;
using System.Windows.Forms;
using System.IO;
using BH.oM.Reflection;
using System.Collections.Generic;
using System.ComponentModel;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        [Description("Import a Python module into the BHoM.")]
        public static PyObject Import(this string moduleName)
        {
            // check if python is installed
            if (!Query.IsPythonInstalled())
            {
                string installMessage = $"Cannot import module {moduleName} because no valid version of Python for the BHoM has been found.\n" +
                "Do you want to install the Python_Toolkit?";
                DialogResult confirmResult = MessageBox.Show(installMessage, "Python not found", MessageBoxButtons.YesNoCancel);

                if (confirmResult == DialogResult.Yes)
                {
                    Output<bool, List<string>> result = Compute.InstallPythonToolkit(true);
                    Reflection.Compute.RecordWarning("Python has been installed, please restart the UI or recompute the script.");
                }
                else
                {
                    string errorMessage = $"Cannot import module {moduleName}" +
                                           "Try installing Python and the Python_Toolkit using the Compute.InstallPythonToolkit component.\n" +
                                           "and the MachineLearning_Toolkit using the Compute.InstallMachineLearning_Toolkit component.\n" +
                                           "If the installation process fails, pleae consider reporting a bug at " +
                                           "https://github.com/BHoM/MachineLearning_Toolkit/issues/new?labels=type%3Abug&template=00_bug.md";
                    throw new Exception(errorMessage);
                }
            }

            if (!m_Initialised)
            {
                // Make sure that the BHoM is loading our bespoke python program
                Compute.SetPythonHome();
                // if python fails to be initialised, it will throw an exception, which can be caught by the TryImport method
                PythonEngine.Initialize();
                m_Initialised = true;
            }
            return PythonEngine.ImportModule(moduleName);
        }


        /***************************************************/
        /**** Private Fields                            ****/
        /***************************************************/

        private static bool m_Initialised = false;

        /***************************************************/

    }
}

