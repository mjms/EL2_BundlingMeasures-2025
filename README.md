# Code and data for *"Bundling Measures for Food Systems Transformation: a global, multimodel assessment"*
[![DOI](https://zenodo.org/badge/1071629437.svg)](https://doi.org/10.5281/zenodo.17289084)

This repository contains the code and data used in our paper *"Bundling Measures for Food Systems Transformation: a global, multimodel assessment"* ([https://doi.org/10.1016/j.lanplh.2025.101339](https://doi.org/10.1016/j.lanplh.2025.101339)). This includes Jupyter Notebooks to generate the main and supplementary figures in the paper, generate Excel sheets that summarize the dataset, and an outline of the data processing pipeline used in the paper.

We used the custom package AgMIP Processing PipeLinE or `applepy`. Note that `applepy` is still in development. The version used here may not be the most current release. Therefore it is important to use the included `applepy` folder in this repository. 

## Set up environment
On the terminal:
1. Clone this repository (`gh repo clone mjms/EL2_BundlingMeasures-2025`)
2. Create Python environment (e.g. `conda env create -n <name for your environment> -f environment.yml`)
3. Activate environment (e.g. `conda activate <name for your envrionment>`)

All the code in this repository is written in Python and runs on Jupyter Notebooks.

## Notebooks included
* `paper-figures.ipynb` : run to replicate main figures and supplementary figures. You may need to change the path to the correct 
* `paper-tables.ipynb` : run to generate Excel sheets that summarizes the dataset providing the ensemble median, and minimum and maximum values for variables and items presented in the paper.
* **NOTE:** The notebook `data-processing.ipynb` is included however it is not executable. This is to provide the user with a template on how to use the `applepy` functions and perform the initial data processing of the data from the raw model submission to the merged dataset provided in the data folder. This includes calculating the individual, interaction, and total effects for the decomposition analysis. In practice, the dataset was updated iteratively over many model submissions. 

## Data 
This dataset includes variables, items, and regions listed in `data/dataset_global-paper.xlsx`
* `global-paper_dataset.csv`: 
  * `'model'` : `['AIM', 'CAPRI', 'ENVISAGE', 'FARM', 'GCAM', 'GLOBIOM', 'IMAGE', 'IMPACT', 'MAGNET','MAgPIE']`
  * `'scenario'`: `['BAU', 'BAU_PROD','BAU_WAST','BAU_DIET','BAU_MITI', 'ELM']`
  * `'region'` : see `data/dataset_global-paper.xlsx` 
  * `'variable'`: see `data/dataset_global-paper.xlsx` 
  * `'item'`: see `data/dataset_global-paper.xlsx`
  * `'unit'` : model units for the variable
  * `'year'` : `[2020, 2050]`
  * `'value'`: absolute value reported by model
  * `'BAU_ref_year'`: base year
  * `'percent_change_BAU_ref_year'`: percentage change from base year
  * `'diff_BAU_ref_year'`: absolute difference between scenario and year from BAU base year
  * `'percent_change_BAU'`: percentage from BAU of the same year
  * `'diff_BAU'`: absolute difference between scenario and year from BAU of the same year
  * `'percent_change_ELM'`: percentage change from ELM of the same year
  * `'diff_ELM'`: absolute difference between scenario and year from ELM of the same year

* `global-paper_decomposition.csv`: wide format to generate summary tables
  * `'individual'` : individual effect of < driver >
  * `'total'` : total effect of < driver >
  * `'interaction'`: interaction effect of < driver >
  * `'model'`: `['AIM', 'CAPRI', 'ENVISAGE', 'FARM', 'GCAM', 'GLOBIOM', 'IMAGE', 'IMPACT', 'MAGNET','MAgPIE']`
  * `'region'`: see `data/dataset_global-paper.xlsx`
  * `'variable'`: see `data/dataset_global-paper.xlsx`
  * `'item'` : see `data/dataset_global-paper.xlsx`
  * `'year'`: `[2020, 2050]`
  * `'unit'` : model units for the variable
  * `'driver'`: `['DIET','PROD','MITI','WAST']`
  * `'normalized'`: Boolean. If `True`, effect is divided by the difference of ELM and BAU. This gives the proportion of the change in ELM that is due to the < driver >. Note that this ratio can be greater than one because of interaction effects with the other drivers. If `False`, the effect is reported as is. 
  * `'value_type'`: `['value','percent_change_BAU','percent_change_BAU_ref_year']` 
  * `'ELM'`: value for ELM for this set of parameters
  * `'BAU'`: value for BAU for this set of parameters
  * `'EL2'`: value for EL2 for this set of parameters (EL2 is equivalent to ELM_MITI, or when only DIET, PROD, and WAST are implemented)
  * `'ELM_driver'`: ELM_< driver > (this equivalent to bundling all the measures EXCEPT the < driver >)
  * `'BAU_driver'`: BAU_< driver > (this is equivalent to only implementing < driver > by itself)
  * `'percent_change_BAU_individual'` : percentage change of individual effect from BAU 2050
  * `'percent_change_BAU_total'`: percentage change of total effect from BAU 2050
  * `'percent_change_BAU_interaction'`: percentage change of interaction effect from BAU 2050

* `global-paper_decomposition_long-format.csv`: the same as `global-paper_decomposition.csv` but in long format. Used for Figure 3
  * `'model'` : `['AIM', 'CAPRI', 'ENVISAGE', 'FARM', 'GCAM', 'GLOBIOM', 'IMAGE', 'IMPACT', 'MAGNET','MAgPIE']`
  * `'region'` : see `data/dataset_global-paper.xlsx` 
  * `'variable'`: see `data/dataset_global-paper.xlsx` 
  * `'item'`: see `data/dataset_global-paper.xlsx`
  * `'unit'` : model units for the variable
  * `'year'` : `[2020, 2050]`
  * `'driver'`: `['DIET','PROD','MITI','WAST']`
  * `'normalized'`: Boolean. If `True`, effect is divided by the difference of ELM and BAU. This gives the proportion of the change in ELM that is due to the < driver >. Note that this ratio can be greater than one because of interaction effects with the other drivers. If `False`, the effect is reported as is. 
  * `'value_type'`: `['value','percent_change_BAU','percent_change_BAU_ref_year']` 
  * `'effect'` : `['total', 'individual', 'interaction']`
  * `'value'` : value based on `value_type` (ie. if value type is 'value' this is reported as the absolute change in < unit >; if value type is in percentage change, this is reported in change in percentage points)

# Authors and Contributors to this work
Marina Sundiang*, Thais Diniz Oliveira, Daniel Mason-D’Croz, Matthew Gibson, Felicitas Beier, Lauren Benavidez, Benjamin Leon Bodirsky, Astrid Bos, Maksym Chepeliev, David Meng-Chuen Chen, Thijs de Lange, Jonathan Doelman, Shahnila Dunston, Stefan Frank, Shinichiro Fujimori, Tomoko Hasegawa, Petr Havlik, Jordan Hristov, Jonas Jägermeyr, Marta Kozicka, Marijke Kuiper, Page Kyle, Hermann Lotze-Campen, Hermen Luchtenbelt, Abhijeet Mishra, Christoph Müller, Gerald Nelson, Amanda Palazzo, Ignacio Pérez Domínguez, Alexander Popp, Ronald Sands, Marco Springmann, Elke Stehfest, Timothy Sulser, Kiyoshi Takahashi, Gianmaria Tassinari, Ferike Thom, Philip Thornton, Kazuaki Tsuchiya, Willem-Jan van Zeist, Hans van Meijl, Dominique van der Mensbrugghe, Detlef Van Vuuren, Hannah H E van Zanten, Isabelle Weindl, Keith Wiebe, Xin Zhao, Mario Herrero

*corresponding author, Department of Global Development, College of Agriculture and Life Science, Cornell University, Ithaca, NY, USA (msundiang@cornell.edu)


