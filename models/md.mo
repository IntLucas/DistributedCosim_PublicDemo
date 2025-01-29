model md
  parameter Real d1 = 1.0;
  parameter Real m1 = 1.0;
  output Real x(start = 0);
  output Real v(start = 0);
  input Real fk;
  input Real springforce;
equation
  der(x) = v;
  der(v) = 1 / m1 * (springforce - d1 * v + fk);
end md;
