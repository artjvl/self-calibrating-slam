import pathlib
import typing as tp

from matplotlib import pyplot as plt
from matplotlib import ticker
from src.framework.analysis.FigureParser import FigureParser


class Plotter(object):
    _fig: tp.Optional[plt.Figure]

    def __init__(self, fig: tp.Optional[plt.Figure]):
        self._fig = fig

    def load(self, name: str) -> None:
        self._fig = FigureParser.load(name)

    def has_fig(self) -> bool:
        return self._fig is not None

    def set_title(
            self,
            title: str,
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        if ax_index is not None:
            ax: plt.Axes = self._fig.axes[ax_index]
            ax.set_title(title)
        else:
            self._fig.suptitle(title)

    def legend(
            self,
            labels: tp.List[str],
            lines: tp.Optional[tp.List[plt.Line2D]] = None,
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        if ax_index is not None:
            ax: plt.Axes = self._fig.axes[ax_index]
            if lines is not None:
                ax.legend(handles=lines, labels=labels)
            else:
                ax.legend(labels=labels)
        else:
            for ax in self._fig.axes:
                if lines is not None:
                    ax.legend(handles=lines, labels=labels)
                else:
                    ax.legend(labels=labels)

    def grid(
            self,
            spacing: tp.Optional[int] = None,
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        ax: plt.Axes
        if ax_index is None:
            for ax in self._fig.axes:
                self.ax_grid(ax, spacing)
        else:
            ax = self._fig.axes[ax_index]
            self.ax_grid(ax, spacing)

    @staticmethod
    def ax_grid(
            ax: plt.Axes,
            spacing: tp.Optional[int] = None
    ) -> None:
        if spacing is not None:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(spacing))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(spacing))
        ax.grid()

    def x_limits(
            self,
            lower: float,
            upper: float,
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        if ax_index is None:
            ax: plt.Axes
            for ax in self._fig.axes:
                ax.set_xlim(lower, upper)
        else:
            ax = self._fig.axes[ax_index]
            ax.set_xlim(lower, upper)

    def y_limits(
            self,
            lower: tp.Optional[float],
            upper: tp.Optional[float],
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        if ax_index is None:
            ax: plt.Axes
            for ax in self._fig.axes:
                ax.set_ylim(lower, upper)
        else:
            ax = self._fig.axes[ax_index]
            ax.set_ylim(lower, upper)

    def save(
            self,
            name: str,
            dpi: float = 200
    ) -> None:
        assert self.has_fig()
        path: pathlib.Path = (FigureParser.path() / f'{name}.png').resolve()
        self._fig.savefig(str(path), dpi=dpi, bbox_inches='tight')

    def show(self) -> None:
        assert self.has_fig()
        self._fig.show()