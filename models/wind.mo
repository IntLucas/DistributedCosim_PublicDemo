model wind
  parameter Real pi = 3.14;
  parameter Real A = 0.0;
  parameter Real p = 1.0;
  parameter Real d = 0.0;
  parameter Real B = 1.0;
  output Real simtime(start = 0);
  output Real windforce;
equation
  der(simtime) = 1.0;
  windforce = A * sin( (2*pi/p)*(simtime - d)) + B;
end wind;
