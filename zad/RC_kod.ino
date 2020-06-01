int PWMpin = 3;
char r;
float U, i,x,y;
float kp = 3.7;
float ki = 0.002;
float kd = 1;
unsigned long currentTime, previousTime;
double elapsedTime;
float error;
float s1, s2;
float lastError;
float out;
float cumError, rateError;
float computePID(float inp,float Setpoint);
  
void setup(){
  pinMode(PWMpin, OUTPUT);
  Serial.begin(9600);

  s2=1;

}

void loop()
{
r=Serial.read();
//r=r-48;
//Serial.print(float(r));
//r=4;
if ((float(r)!=57) && (float(r)>0)) {
s1=float(r);
s1=s1-48;
//Serial.print(s1);
}
 
	
    U=analogRead(A0);
    out = computePID(U*0.004882, s1);
    if (out>5){
     out=5;
    }
    if (out<0){
     out=0;
    }
    analogWrite(PWMpin,(out)*51);
//Serial.println(U*0.004882);

x=U*0.004882;
y=U*0.0088;
//Serial.print(x);
//Serial.println(float(r));
if ((float(r)>0)) {
    Serial.print(x);
	Serial.print(",");
	Serial.println(y);
	
}
    delay(100);



}

float computePID(float inp,float Setpoint){     
        currentTime = millis();                
        elapsedTime = (double)(currentTime - previousTime);        
        
        error = Setpoint - inp;                               
        cumError += error * elapsedTime;                
        rateError = (error - lastError)/elapsedTime;   
 
        float out = kp*error + ki*cumError + kd*rateError;                        
 
        lastError = error;                                
        previousTime = currentTime;                        
  
        return out;        
}