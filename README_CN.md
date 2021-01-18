

# MEPplot
 [English](README.md)  [日本語](README_JP.md)

<a href="https://explosion.ai"><img src=".\ui\Logo.png"  width="225" height="185" align="right" /></a>

一个在势能面（自由能面）上绘制最小能量路径的程序。 本程序基于弦方法(string method)。 更多细节，请参考如下论文 (Phys. Rev. B **66**, 052301 – Published 12 August 2002) 





## 下载与安装

在如下链接里找到 `.rar` 文件：

https://github.com/chenxin199261/MEPplot/releases

或者

https://mega.nz/folder/hsVzVSKT#3IEzoJZzkmEQZJACTAEcMQ

对于身处中国大陆的用户 (GitHub非常慢), 请用如下链接下载:

https://n459.com/file/30374101-473325811  （提取码;111111）

下载rar文件并解压， 你会得到如下三个文件，

* MEPplot.bat :MEPplot程序的入口, 可执行脚本.
* example: 势能面模板.
* main: 程序文件.

## 用法

点击二进制文件 `MEPplot.exe`。 你会看到如下界面。 请跟随指引一步步完成绘制。

<img src=".\Readme-figures\R2.png" alt="R2"  />

#### 1. 准备势能面数据文件

你的二维势能面文件应该遵循严格格式，文件包含三列  (X坐标, Y坐标 和能量）。如下：

```
  -0.88235    1.99224   30.64485
   1.23646   -0.78346  420.58113
   1.03326    0.21343   18.23895
  -1.28864    1.87634   23.34170
   0.22373    0.08548  -79.56263
   0.97433    0.60216  119.97031
   0.03879   -0.50717   55.13104
...
```

模板也可以在example文件夹中找到。 



#### 2. 载入势能面数据文件并且绘制二维势能面

点击右上角的`Open...` 按钮并选择你的势能面文件。势能面会立即出现在 `plot window` 中。自动生成的图像可能并不适宜观察到最低点与鞍点。用户需要修改 `PES plot control` 面板中的相关参数。

<img src=".\Readme-figures\R3.png" alt="R3"  />

* **Max. V**: 等高面中的最大值。大于 *Max. V* 的数据点会被屏蔽掉。. 
* **Min. V**: 等高面中的最小值。小于 *Mix. V* 的数据点会被屏蔽掉。 (不要修改、否则你会看不到最小值点)
* **Level**: 势能面上的等高线数目. 
* **Cmap**：图形风格.

点击 `Regenrate` 按钮你会看到新的势能面。如果你把它们弄乱了， 点击`Reset plot`。



#### 3. 寻找能量最低路径

首先，用户需要提供”弦“的初始猜测。准确的初始猜测能让你更快得到结果。可以通过珠子来定义”弦“ (最少两个珠子)。 点击 `Guess beads`，并在如下对话框中输入初始猜测珠子的坐标（X、Y）。



<img src=".\Readme-figures\R4.png" alt="R4"  />

在本例中， 我们用四个珠子来定义初始”弦“。 点击`OK`， 初始弦（黑实线）会在势能面上被绘制。 

<img src=".\Readme-figures\R5.png" alt="R5"  />

本程序会提供优化最低能量路径的默认参数。建议您直接使用默认参数。 如果收敛失败， 你可以调整这些参数。

<img src=".\Readme-figures\R6.png" alt="R6"  />

* **No. of Beads**: 珠子的数目。 这里定义了弦上有多少个珠子， 珠子越多越精确。
* **Max. iter**: 最大迭代数目。如果优化迭代步数超过 *Max. iter* 值， 优化进程便会停止。 
* **Step size**:  *Step size* 值决定了梯度下降的步长。  



点击 `Run` ， 优化过程会开始。 初始猜测的”弦“会被优化为最低能量路径。优化过程可以在绘图窗口中可视化。 当你在记录窗口看到  `Converged !` ，意味着优化结束并且得到了最低能量路径。 



#### 4. 显示结果

最后, 在 `MEP searching` 界面点击 `Show` 按钮。 你会看到如下结果。

 <img src=".\Readme-figures\R7.png" alt="R7"  />

点击`Export data` 按钮，最低能量路径上珠子的坐标以及对应的能里会被输出到一个文件中来进行后续应用。





## 技巧

1. 当完成一轮优化后，未收敛（或收敛）的珠子会被设定为初始猜测。用户可以继续点击`run` 以使优化过程收敛。 你也可以点击 `Guess beads` 来生成新的初始猜测。
2. 如果”弦“不停振荡， 尝试减小 `step size` 数值。
3. 如果”弦“上珠子移动十分慢， 试着增大 `step size` 数值。
4. 负的 `step size` 值，可以得到”最高“能量路径。



## 依赖关系

* pyqt5: 5.15
* Matplotlib: 3.1.3
* numpy: 1.15
* scipy:1.5.4



## License

MEPplot: A GUI program for plotting Minimal energy path on potential energy surface. 
Copyright (C)  2020 Xin Chen

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.