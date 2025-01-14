import math
from typing import Optional, Union

import tensorrt as trt
from torch.fx.node import Target
from torch_tensorrt.dynamo.conversion import impl
from torch_tensorrt.dynamo.conversion._ConversionContext import ConversionContext
from torch_tensorrt.dynamo.conversion.converter_utils import SourceIR
from torch_tensorrt.fx.types import TRTTensor


def scaled_dot_product_attention(
    ctx: ConversionContext,
    target: Union[Target, str],
    source_ir: Optional[SourceIR],
    name: str,
    query: TRTTensor,
    key: TRTTensor,
    value: TRTTensor,
) -> TRTTensor:
    mm = impl.matmul.matrix_multiply(
        ctx,
        target,
        source_ir,
        name + "_mm",
        query,
        key,
        other_matrix_op=trt.MatrixOperation.TRANSPOSE,
    )
    div = impl.elementwise.div(
        ctx,
        target,
        source_ir,
        name + "_scale",
        mm,
        math.sqrt(query.shape[-1]),
    )
    softmax = impl.normalization.softmax(
        ctx, target, source_ir, name + "_softmax", div, -1
    )
    out = impl.matmul.matrix_multiply(
        ctx,
        target,
        source_ir,
        name + "_out",
        softmax,
        value,
    )

    return out
