# jh-get

A JupyterHub service that provides a URL endpoint which downloads a notebook to a user's Jupyter instance and forwards the user's browser to the downloaded notebook. Authentication is handled by JupyterHub. To use, navigate to
```
{jupyterhub base url}/services/jh-get/?path={path to .ipynb file}
```

To install, ensure `jh-get` is a listed service in your `jupyterhub_config.py`, and that `JUPYTERHUB_USER_PATH` is set properly.