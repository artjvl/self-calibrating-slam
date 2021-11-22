import pathlib
import typing as tp

from matplotlib import pyplot as plt
from matplotlib import ticker
from src.framework.analysis.plot.FigureParser import FigureParser


class Plotter(object):
    _fig: tp.Optional[plt.Figure]

    def __init__(self, fig: tp.Optional[plt.Figure] = None):
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

    def x_label(
            self,
            label: str,
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        if ax_index is not None:
            ax: plt.Axes = self._fig.axes[ax_index]
            ax.set_xlabel(label)
        else:
            for ax in self._fig.axes:
                ax.set_xlabel(label)

    def y_label(
            self,
            label: str,
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        if ax_index is not None:
            ax: plt.Axes = self._fig.axes[ax_index]
            ax.set_ylabel(label)
        else:
            for ax in self._fig.axes:
                ax.set_ylabel(label)

    def grid(
            self,
            x_spacing: tp.Optional[float] = None,
            y_spacing: tp.Optional[float] = None,
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        ax: plt.Axes
        if ax_index is None:
            for ax in self._fig.axes:
                self.ax_spacing(ax, x_spacing, y_spacing)
                ax.grid()
        else:
            ax = self._fig.axes[ax_index]
            self.ax_spacing(ax, x_spacing, y_spacing)
            ax.grid()

    def spacing(
            self,
            x_spacing: tp.Optional[float] = None,
            y_spacing: tp.Optional[float] = None,
            ax_index: tp.Optional[int] = None
    ) -> None:
        assert self.has_fig()
        ax: plt.Axes
        if ax_index is None:
            for ax in self._fig.axes:
                self.ax_spacing(ax, x_spacing, y_spacing)
        else:
            ax = self._fig.axes[ax_index]
            self.ax_spacing(ax, x_spacing, y_spacing)

    def ax_spacing(
            self,
            ax: plt.Axes,
            x_spacing: tp.Optional[float] = None,
            y_spacing: tp.Optional[float] = None
    ) -> None:
        if x_spacing is not None:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(x_spacing))
        if y_spacing is not None:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(y_spacing))

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
            dpi: float = 300
    ) -> None:
        assert self.has_fig()
        path: pathlib.Path = (FigureParser.path() / f'{name}.png').resolve()
        self._fig.savefig(str(path), dpi=dpi, bbox_inches='tight')

    def show(self) -> None:
        assert self.has_fig()
        self._fig.show()