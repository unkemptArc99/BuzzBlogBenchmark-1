## Setting up your environment

The BuzzBlogBenchmark uses Anaconda python package manager to take care of all the python package requirements. To install Anaconda, you simply have to download a shell script from the [Anaconda Documentation](https://docs.anaconda.com/anaconda/install/linux/), where you will also find the exact steps for installing the environment.

TIP - On step 7, do initialize the Anaconda3 by running `conda init` through the installer script. But then on step 11, diable the `auto_activate_base` config in Anaconda.

After you have installed Anaconda, simply create the environment `bbb_pyenv` from the `.yml` file in the folder `analysis/environment` by running the following commands -
```
conda env create -f analysis/environment/buzzblogbenchmark_pythonEnv.yml
```

After creation of the environment, whenever you want to work on BuzzBlogBenchmark, simply run `conda activate bbb_pyenv`. After your work is finished, you can deactivate it by `conda deactivate`.

If you wish to remove this environment from your system, then simply run `conda env remove -n bbb_pyenv` after deactivativating the environment.