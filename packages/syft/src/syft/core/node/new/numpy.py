# stdlib
from typing import Any

# third party
import numpy as np

# relative
from ....core.node.common.node_table.syft_object import SYFT_OBJECT_VERSION_1
from ...common.serde.serializable import serializable
from .action_object import ActionObject
from .action_types import action_types

# @serializable(recursive_serde=True)
# class NumpyArrayObjectPointer(ActionObjectPointer):
#     _inflix_operations = ["__add__", "__sub__", "__eq__", "__mul__"]
#     __canonical_name__ = "NumpyArrayObjectPointer"
#     __version__ = SYFT_OBJECT_VERSION_1

#     # 🟡 TODO 17: add state / allowlist inheritance to SyftObject and ignore methods by default
#     __attr_state__ = [
#         "id",
#         "node_uid",
#         "parent_id",
#     ]

#     def get_from(self, domain_client) -> Any:
#         return domain_client.api.services.action.get(self.id).syft_action_data


class NumpyArrayObjectPointer:
    pass


def numpy_like_eq(left: Any, right: Any) -> bool:
    result = left == right
    if isinstance(result, bool):
        return result

    if hasattr(result, "all"):
        return (result).all()
    return bool(result)


# 🔵 TODO 7: Map TPActionObjects and their 3rd Party types like numpy type to these
# classes for bi-directional lookup.
@serializable(recursive_serde=True)
class NumpyArrayObject(ActionObject, np.lib.mixins.NDArrayOperatorsMixin):
    __canonical_name__ = "NumpyArrayObject"
    __version__ = SYFT_OBJECT_VERSION_1

    syft_internal_type = np.ndarray
    syft_pointer_type = NumpyArrayObjectPointer
    syft_passthrough_attrs = []
    syft_dont_wrap_attrs = ["dtype"]

    def __eq__(self, other: Any) -> bool:
        # 🟡 TODO 8: move __eq__ to a Data / Serdeable type interface on ActionObject
        if isinstance(other, NumpyArrayObject):
            return (
                numpy_like_eq(self.syft_action_data, other.syft_action_data)
                and self.syft_pointer_type == other.syft_pointer_type
            )
        return self == other

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        print("__array_ufunc__", ufunc, method, inputs, kwargs)

        inputs = tuple(
            np.array(x.syft_action_data, dtype=x.dtype)
            if isinstance(x, NumpyArrayObject)
            else x
            for x in inputs
        )

        result = getattr(ufunc, method)(*inputs, **kwargs)
        if type(result) is tuple:
            return tuple(
                NumpyArrayObject(syft_action_data=x, dtype=x.dtype, shape=x.shape)
                for x in result
            )
        else:
            return NumpyArrayObject(
                syft_action_data=result, dtype=result.dtype, shape=result.shape
            )


# @transform(NumpyArrayObject, NumpyArrayObjectPointer)
# def np_array_to_pointer() -> List[Callable]:
#     return []


np_array = np.array([1, 2, 3])
action_types[type(np_array)] = NumpyArrayObject
