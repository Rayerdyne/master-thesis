# Neural network

Re-writing of Carla's work, for the most part

## Files

- [`config.py`](config.py) holds the configuration of the network to be trained, name, data to use, inputs and outputs
- [`model.py`](model.py) holds the description of the model to be trained, via the `build_model` function
- [`train.py`](train.py) executes the tuner search for the best model and training of that best model
- [`view.py`](view.py) holds different utilities to view the results of some model and its performances.
    - use `view.py --surface <in1> <in2> <out>` to create a 3d surface of the out-th output depending on the in1 and in2-th inputs. The other inputs are constant and parameterizable with sliders.