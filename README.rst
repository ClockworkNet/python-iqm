python-iqm
==========

Interquartile Mean pure-Python module. It contains two classes:

1. DictIQM
2. MovingIQM


DictIQM
=======

This class is efficient for datasets in which many numbers are repeated. It
should not be used for large datasets with a uniform distribution. The
trade-off between accuracy and memory usage can be manged with its
`round_digits` argument.

Usage
-----

.. code:: python

    from iqm import DictIQM
    import sys

    diqm = DictIQM(round_digits=-1, tenth_precise=True)
    for line in open("source1_numbers_list.txt", "r"):
        diqm("source1", line)

    print "# {:12,.2f}    Dict IQM".format(diqm.final_report("source1"))


MovingIQM
=========

This class sacrifices accuracy for speed and low memory usage.

Usage
-----

.. code:: python

    from iqm import MovingIQM
    import sys

    miqm = MovingIQM(1000)
    for line in open("source1_numbers_list.txt", "r"):
        miqm("source1", line)

    print "# {:12,.2f}    Moving IQM".format(miqm.final_report("source1"))


License
=======

See `LICENSE.txt`_ (`MIT License`_).

.. _`LICENSE.txt`:
   https://github.com/ClockworkNet/python-iqm/blob/master/LICENSE.txt
.. _`MIT License`: http://www.opensource.org/licenses/MIT
