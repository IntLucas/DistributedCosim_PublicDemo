model spring
  parameter Real c1 = 1.0;
  input Real x;
  output Real springforce;
equation
  springforce = - c1 * x;
end spring;
