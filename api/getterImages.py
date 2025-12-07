import pandas as pd
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse
import io
import numpy as np


def get_image_from_table(res, isImage: bool):
    if res == []:
        return res
    if isImage:
        df = pd.DataFrame([dict(row._mapping) for row in res])
        num_rows = len(df)
        num_cols = len(df.columns)

        fig_height = max(3, num_rows * 0.4 + 2)

        col_widths = [max(len(str(col)), 10) for col in df.columns]
        for col in df.columns:
            max_len = max([len(str(x)) for x in df[col]])
            col_idx = df.columns.get_loc(col)
            col_widths[col_idx] = max(col_widths[col_idx], max_len)

        fig_width = max(6, sum(col_widths) * 0.15)

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis('tight')
        ax.axis('off')

        font_size = max(8, min(12, 100 / (num_rows)))

        cell_data = []
        for i in range(len(df)):
            row = []
            for value in df.iloc[i]:
                text = str(value)
                if len(text) > 30:
                    words = text.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) + 1 <= 30:
                            current_line += (" " if current_line else "") + word
                        else:
                            lines.append(current_line)
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    text = "\n".join(lines)
                row.append(text)
            cell_data.append(row)

        header_color = '#2E86AB'
        row_colors = ['#F5F5F5', '#FFFFFF']
        text_color = '#333333'
        edge_color = '#CCCCCC'

        header_colors = plt.cm.Blues(np.linspace(0.6, 0.3, num_cols))

        table = ax.table(
            cellText=cell_data,
            colLabels=df.columns,
            cellLoc='center',
            loc='center',
            colWidths=[0.4 * (w / max(col_widths)) for w in col_widths]
        )

        table.auto_set_font_size(False)
        table.set_fontsize(font_size)

        for j in range(num_cols):
            cell = table[(0, j)]
            cell.set_facecolor(header_colors[j])
            cell.set_text_props(weight='bold', color='white', ha='center')
            cell.set_edgecolor(edge_color)
            cell.set_linewidth(1.5)
            cell.PAD = 0.1

        for i in range(num_rows):
            for j in range(num_cols):
                cell = table[(i + 1, j)]
                cell.set_facecolor(row_colors[i % len(row_colors)])
                cell.set_text_props(color=text_color, ha='center')
                cell.set_edgecolor(edge_color)
                cell.set_linewidth(0.5)

                try:
                    val = float(df.iloc[i, j])
                    if val > 0:
                        intensity = min(0.95, 0.7 + val / 100)
                        cell.set_facecolor(plt.cm.Greens(0.3 + intensity * 0.4))
                    elif val < 0:
                        intensity = min(0.95, 0.7 + abs(val) / 100)
                        cell.set_facecolor(plt.cm.Reds(0.3 + intensity * 0.4))
                except (ValueError, TypeError):
                    pass

                cell_text = cell.get_text().get_text()
                num_lines = cell_text.count('\n') + 1
                cell.set_height(0.1 * num_lines)
                cell.PAD = 0.05

        for pos, cell in table.get_celld().items():
            cell.set_linewidth(0.8)


        table.scale(1, 1.5)

        fig.patch.set_facecolor('#F8F9FA')
        ax.set_facecolor('#F8F9FA')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight',
                    pad_inches=0.3, facecolor=fig.get_facecolor(),
                    edgecolor='none', transparent=False)
        plt.close(fig)
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=colorful_table.png"}
        )
    else:
        return [list(el) for el in res]