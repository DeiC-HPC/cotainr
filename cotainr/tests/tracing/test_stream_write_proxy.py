"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import io

import pytest

from cotainr.tracing import StreamWriteProxy


class TestConstructor:
    def test_attributes(self):
        stream = io.StringIO()
        stream_write_proxy = StreamWriteProxy(stream=stream)
        assert stream_write_proxy._stream is stream
        assert stream_write_proxy.true_stream_write == stream.write


class TestWrite:
    def test_write_when_stream_write_changed(self):
        stream = io.StringIO()
        stream_write_proxy = StreamWriteProxy(stream=stream)
        stream.write = lambda s: ""
        stream.write("some text to disappear ")
        stream_write_proxy.write("some text to keep")
        assert stream.getvalue() == "some text to keep"

    def test_write_when_stream_write_unchanged(self):
        stream = io.StringIO()
        stream_write_proxy = StreamWriteProxy(stream=stream)
        stream.write("some text to keep - ")
        stream_write_proxy.write("some text to keep")
        assert stream.getvalue() == "some text to keep - some text to keep"


class TestGetAttr:
    def test_failing_attribute_lookup_delegation(self):
        stream = io.StringIO("some text 6021")
        stream_write_proxy = StreamWriteProxy(stream=stream)
        with pytest.raises(
            AttributeError,
            match=r"StringIO' object has no attribute 'some_nonsense_attribute_6021'$",
        ):
            _ = stream_write_proxy.some_nonsense_attribute_6021

    def test_successful_attribute_lookup_delegation(self):
        stream = io.StringIO("some text 6021")
        stream_write_proxy = StreamWriteProxy(stream=stream)
        assert "getvalue" not in dir(stream_write_proxy)
        assert stream_write_proxy.getvalue() == "some text 6021"
