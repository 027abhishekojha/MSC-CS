import java.io.*;
import java.net.*;

class Client {
	public static void main(String[] args) throws Exception {
		InputStreamReader isr = new InputStreamReader(System.in);
		BufferedReader keyboard = new BufferedReader(isr);
		Socket s = new Socket("localhost", 2222);
		BufferedReader br1 = new BufferedReader(new InputStreamReader(s.getInputStream()));
		PrintWriter pw = new PrintWriter((s.getOutputStream()));
		while (true) {
			System.out.println("Enter Send/Quit/Receive");
			String k = keyboard.readLine();

			switch (k.charAt(0)) {
				case 'S':
				case 's':
					String sendmsg = keyboard.readLine();
					pw.println(sendmsg);
					pw.flush();
					break;
				case 'R':
				case 'r':
					String recvmsg = br1.readLine();
					System.out.println(recvmsg);
					break;
				case 'Q':
				case 'q':
					System.exit(0);

			}

		}

	}
}
