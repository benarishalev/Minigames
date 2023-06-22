Public Class Form1

    Dim rnd As New Random

    Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load

    End Sub
    Private Sub Form1_KeyDown(ByVal sender As Object, ByVal e As KeyEventArgs) Handles MyBase.KeyDown
        If e.KeyCode = Keys.Space Then

            PictureBox1.Top -= 30



        End If

    End Sub

    Private Sub Timer1_Tick(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Timer1.Tick
        PictureBox1.Top += 4
        Panel2.Left -= 5
        Panel3.Left -= 5
    End Sub

    Private Sub Label1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Label1.Click



        Dim randomlocation As Integer = rnd.Next(1, 3)
        Label1.Text = randomlocation
        If randomlocation = 1 Then

            Panel2.Left = 307
            Panel2.Top = -4

            Panel3.Left = 307
            Panel3.Top = 286
        End If
        If randomlocation = 2 Then

            Panel2.Left = 207
            Panel2.Top = -20

            Panel3.Left = 207
            Panel3.Top = 250
        End If

    End Sub
End Class
