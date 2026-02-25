from python_toolkit.bhom_tkinter.widgets.label import Label
from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow

root = BHoMBaseWindow()
root.update()
label = Label(root.content_frame, text='initial')
label.build()
print('before:', label.label.cget('text'))
label.set('updated')
print('after set:', label.label.cget('text'))
frames=['◐','◓','◑','◒']
for i,ch in enumerate(frames):
    label.set(ch)
    print(f'frame {i} =>', label.label.cget('text'))
root.destroy()
