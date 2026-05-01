# 00_renv_restore.R

# Ensure renv is installed and load the project environment

if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv", repos = repos)
}

# yaml is needed by renv to parse Rmd dependencies
if (!requireNamespace("yaml", quietly = TRUE)) {
  install.packages("yaml", repos = repos)
}

# Restore the project's package environment
renv::activate()
renv::restore()

print(renv::status())