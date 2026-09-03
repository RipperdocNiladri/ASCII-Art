"""Registry for the built-in procedural demonstrations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from . import blackhole, cube, donut, planet, sphere

RenderFunction = Callable[[int, int, int, str], str]


@dataclass(frozen=True)
class Demo:
    name: str
    description: str
    default_width: int
    height_ratio: float
    render: RenderFunction


DEMOS = {
    demo.name: demo
    for demo in (
        Demo("cube", "Rotating filled cube with lighting and depth buffering", 80, 0.44, cube.render_frame),
        Demo("sphere", "Mathematically shaded rotating sphere", 80, 0.44, sphere.render_frame),
        Demo("donut", "Parametric torus with lighting and depth buffering", 80, 0.44, donut.render_frame),
        Demo("planet", "Procedural planet with terrain and atmospheric rim", 90, 0.42, planet.render_frame),
        Demo("blackhole", "Stylized accretion disk, stars, and photon ring", 100, 0.42, blackhole.render_frame),
    )
}


def get_demo(name: str) -> Demo:
    try:
        return DEMOS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown demo: {name}") from exc
