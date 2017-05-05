[![Build Status](https://api.travis-ci.org/allenai/deep_qa.svg?branch=master)](https://travis-ci.org/allenai/deep_qa)
[![Documentation Status](https://readthedocs.org/projects/deep-qa/badge/?version=latest)](http://deep-qa.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/allenai/deep_qa/branch/master/graph/badge.svg)](https://codecov.io/gh/allenai/deep_qa)

# WARNING

This is unreleased code!  We're at the pre-alpha stage, things could change, and there are still
a lot of rough edges.  This grew out of some research code, and we think it'll be pretty useful
generally, but we're still working on making it easily usable by people outside of our group.  Feel
free to submit issues for problems that arise so that we're aware of them, but we're not to the
point of having a supported release yet.

# DeepQA

DeepQA is a library for doing high-level NLP tasks with deep learning, particularly focused on
various kinds of question answering.  DeepQA is built on top of [Keras](https://keras.io) and
[TensorFlow](https://www.tensorflow.org/), and can be thought of as a better interface to these
systems that makes NLP easier.

Specifically, this library provides the following benefits over plain Keras / tensorflow:

- It is hard to get NLP right in Keras.  There are a lot of issues around padding sequences and
  masking that are not handled well in the main Keras code, and we have well-tested code that does
the right thing for, e.g., computing attentions over padded sequences, padding all training
instances to the same lengths (possibly dynamically by batch, to minimize computation wasted on
padding tokens), or distributing text encoders across several sentences or words.
- We provide a nice, consistent API around building NLP models in Keras.  This API has
  functionality around processing data instances, embedding words and/or characters, easily getting
various kinds of sentence encoders, and so on.  It makes building models for high-level NLP tasks
easy.
- We provide a nice interface to training, validating, and debugging Keras models.  It is very easy
  to experiment with variants of a model family, just by changing some parameters in a JSON file.
For example, the particulars of how words are represented, either with fixed GloVe vectors,
fine-tuned word2vec vectors, or a concatenation of those with a character-level CNN, are all
specified by parameters in a JSON file, not in your actual code.  This makes it trivial to switch
the details of your model based on the data that you're working with.
- We have implemented a number of state-of-the-art models, particularly focused around question
  answering systems (though we've dabbled in models for other tasks, as well).  The actual model
code for these systems is typically 50 lines or less.


## Working in a clone of DeepQA

To train or evaluate a model using a clone of the DeepQA repository, the recommended entry point is
to use the [`run_model.py`](./scripts/run_model.py) script.  The first argument to that script
is a parameter file, described more below.  The second argument determines the behavior, either
training a model or evaluating a trained model against a test dataset.  Current valid options for
the second argument are `train` and `test` (omitting the argument is the same as passing `train`).

Parameter files specify the model class you're using, model hyperparameters, training details,
data files, data generator details, and many other things.  You can see example parameter files in
the [examples directory](./example_experiments).  You can get some notion of what parameters are
available by looking through the [documentation](http://deep-qa.readthedocs.io).

Actually training a model will require input files, which you need to provide.  We have a companion
library, [DeepQA Experiments](https://github.com/allenai/deep_qa_experiments), which was
originally designed to produce input files and run experiments, and can be used to generate
required data files for most of the tasks we have models for.  We're moving towards putting the
data processing code directly into DeepQA, so that DeepQA Experiments is not necessary, but for
now, getting training data files in the right format is most easily [done with DeepQA
Experiments](https://github.com/allenai/deep_qa/issues/328#issuecomment-298176527).


## Using DeepQA as a library

If you are using DeepQA as a library in your own code, it is still straightforward to run your
model.  Instead of using the [`run_model.py`](./scripts/run_model.py) script to do the
training/evaluation, you can do it yourself as follows:

```
from deep_qa import run_model, evaluate_model, load_model, score_dataset

# Train a model given a json specification
run_model("/path/to/json/parameter/file")


# Load a model given a json specification
loaded_model = load_model("/path/to/json/parameter/file")
# Do some more exciting things with your model here!


# Get predictions from a pre-trained model on some test data specified in the json parameters.
predictions = score_dataset("/path/to/json/parameter/file")
# Compute your own metrics, or do beam search, or whatever you want with the predictions here.


# Compute Keras' metrics on a test dataset, using a pre-trained model.
evaluate_model("/path/to/json/parameter/file", ["/path/to/data/file"])
```

The rest of the usage guidelines, examples, etc., are the same as when [working in a clone of the
repository](#working-in-a-clone-of-deepqa).


## Implementing your own models

To implement a new model in DeepQA, you need to subclass `TextTrainer`.  There is
[documentation](http://deep-qa.readthedocs.io/en/latest/training/text_trainer.html) on what is
necessary for this; see in particular the [Abstract
methods](http://deep-qa.readthedocs.io/en/latest/training/text_trainer.html#abstract-methods)
section.  For a simple example of a fully functional model, see the [simple sequence
tagger](./deep_qa/models/sequence_tagging/simple_tagger.py), which has about 20 lines of actual
implementation code.

In order to train, load and evaluate models which you have written yourself, simply pass an
additional argument to the functions above and remove the `model_class` parameter from your json
specification.  For example:
```
from deep_qa import run_model
from .local_project import MyGreatModel

# Train a model given a json specification (without a "model_class" attribute).
run_model("/path/to/json/parameter/file", model_class=MyGreatModel)
```

If you're doing a new task, or a new variant of a task with a different input/output specification,
you probably also need to implement an [`Instance`](./deep_qa/data/instances/instance.py) type.
The `Instance` handles reading data from a file and converting it into numpy arrays that can be
used for training and evaluation.  This only needs to happen once for each input/output spec.


## Organization

DeepQA is organised into the following main sections:

-   `common`: Code for parameter parsing, logging and runtime checks.
-   `contrib`: Related code for experiments and untested layers, models and features. Generally
    untested.
-   `data`: Indexing, padding, tokenisation, stemming, embedding and general dataset manipulation
    happens here.
-   `layers`: The bulk of the library. Use these Layers to compose new models. Some of these Layers
    are very similar to what you might find in Keras, but altered slightly to support arbitrary
dimensions or correct masking.
-   `models`: Frameworks for different types of task. These generally all extend the TextTrainer
    class which provides training capabilities to a DeepQaModel. We have models for Sequence
Tagging, Entailment, Multiple Choice QA, Reading Comprehension and more. Take a look at the READMEs
under `model` for more details - each task typically has a README describing the task definition.
-   `tensors`: Convenience functions for writing the internals of Layers.  Will almost exclusively be
    used inside Layer implementations.
-   `training`: This module does the heavy lifting for training and optimisation. We also wrap the
    Keras Model class to give it some useful debugging functionality.

The `data` and `models` sections are, in turn, structured according to what task they are intended
for (e.g., text classification, reading comprehension, sequence tagging, etc.).  This should make
it easy to see if something you are trying to do is already implemented in DeepQA or not.

## Implemented models

DeepQA has implementations of state-of-the-art methods for a variety of tasks.  Here are a few of
them:

#### Reading comprehension

- The attentive reader, from [Teaching Machines to Read and
  Comprehend](https://www.semanticscholar.org/paper/Teaching-Machines-to-Read-and-Comprehend-Hermann-Kocisk%C3%BD/2cb8497f9214735ffd1bd57db645794459b8ff41),
by Hermann and others
- Gated Attention Reader from [Gated Attention Readers for Text
  Comprehension](https://www.semanticscholar.org/paper/Gated-Attention-Readers-for-Text-Comprehension-Dhingra-Liu/200594f44c5618fa4121be7197c115f78e6e110f),
- Bidirectional Attention Flow, from [Bidirectional Attention Flow for Machine
  Comprehension](https://www.semanticscholar.org/paper/Bidirectional-Attention-Flow-for-Machine-Seo-Kembhavi/007ab5528b3bd310a80d553cccad4b78dc496b02),

#### Entailment

- Decomposable Attention, from [A Decomposable Attention Model for Natural Language
  Inference](https://www.semanticscholar.org/paper/A-Decomposable-Attention-Model-for-Natural-Parikh-T%C3%A4ckstr%C3%B6m/07a9478e87a8304fc3267fa16e83e9f3bbd98b27),

#### Memory networks

- The original MemNN, from [Memory Networks](https://arxiv.org/abs/1410.3916), by Weston, Chopra
  and Bordes
- [End-to-end memory
  networks](https://www.semanticscholar.org/paper/End-To-End-Memory-Networks-Sukhbaatar-Szlam/10ebd5c40277ecba4ed45d3dc12f9f1226720523),
by Sukhbaatar and others
- [Dynamic memory
  networks](https://www.semanticscholar.org/paper/Ask-Me-Anything-Dynamic-Memory-Networks-for-Kumar-Irsoy/04ee77ef1143af8b19f71c63b8c5b077c5387855),
  by Kumar and others
- DMN+, from [Dynamic Memory Networks for Visual and Textual Question
  Answering](https://www.semanticscholar.org/paper/Dynamic-Memory-Networks-for-Visual-and-Textual-Xiong-Merity/b2624c3cb508bf053e620a090332abce904099a1),
by Xiong, Merity and Socher

## Datasets

This code allows for easy experimentation with the following datasets:

- [AI2 Elementary school science questions (no diagrams)](http://allenai.org/data.html)
- [The Facebook Children's Book Test dataset](https://research.facebook.com/research/babi/)
- [The Facebook bAbI dataset](https://research.facebook.com/research/babi/)
- [The NewsQA dataset](https://datasets.maluuba.com/NewsQA)
- [The Stanford Question Answering Dataset (SQuAD)](https://rajpurkar.github.io/SQuAD-explorer/)
- [The Who Did What dataset](https://tticnlp.github.io/who_did_what/)

Note that the data processing code for most of this currently lives in [DeepQA
Experiments](https://github.com/allenai/deep_qa_experiments), however.

## Contributing

If you use this code and think something could be improved, pull requests are very welcome. Opening
an issue is ok, too, but we're a lot more likely to respond to a PR. The primary maintainer of this
code is [Matt Gardner](https://matt-gardner.github.io/), with a lot of help from [Pradeep
Dasigi](http://www.cs.cmu.edu/~pdasigi/) (who was the initial author of this codebase), [Mark
Neumann](http://markneumann.xyz/) and [Nelson Liu](http://nelsonliu.me/).

A note on issues: we are a very small team, and our focus is on getting research done, not on
building this library.  We do not have anyone dedicated full-time to maintaining and improving
this code.  As such, we generally do not have bandwidth to solve your problems.  Sorry.  The code
is well tested and works on our continuous integration server, so if the tests do not pass in your
environment, there is something wrong with your environment, not the code.  Please only submit
issues _after_ having made sure the tests pass, and trying to figure out the issue yourself.  In
your issue, explain clearly what the problem is and what you tried to do to fix it, including
commands run and full stack traces.  You're a whole lot more likely to actually get help that way.

## License

This code is released under the terms of the [Apache 2
license](https://www.apache.org/licenses/LICENSE-2.0).
