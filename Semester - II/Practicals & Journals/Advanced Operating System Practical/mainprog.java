class  ABC
{
	synchronized void print()
	{   int a=0;
	   System.out.println("hi");
	   System.out.println("I");
	   System.out.println("am");
	   ++a;
	   try{
	   Thread.sleep(500);
	   }
	   catch(Exception e)
		{
			
		}
	   
	   System.out.println("Abhishek Ojha Roll No 027 From MS.CS Learning"+a);
	   System.out.println("Java");
	   }

}
class myprog extends Thread 
{  ABC ob1;
myprog(ABC ob)
	{
	ob1=ob;
	}
public void run()
	{
    ob1.print();
	}

}
class mainprog
{
  public static void main(String args[])
	{
	ABC ob = new ABC();
    myprog t1=new myprog(ob);
	    myprog t2=new myprog(ob);
		t1.start();
		t2.start();
	}
}

