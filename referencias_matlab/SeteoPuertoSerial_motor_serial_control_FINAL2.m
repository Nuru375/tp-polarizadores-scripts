   function PuertoSerial = SeteoPuertoSerial_motor_serial_control_FINAL2(port)
   %port = 'COM3';
   
   global PuertoSerial
   
   if nargin == 0
       fclose(PuertoSerial);
       delete(PuertoSerial);
       clear PuertoSerial;
       disp('Puerto serie cerrado');return
   end
   clc
   % -------- LIMPIEZA TOTAL --------
   delete(instrfindall);
   % -------- CONFIG SERIAL --------
   
   baud = 19200;
   PuertoSerial = serial(port,'BaudRate',baud,'Timeout',5,'Terminator','LF');
   fopen(PuertoSerial);
   pause(3);            % reset Arduino
   flushinput(PuertoSerial);
   fprintf('Conectado a %s\n', port);
   fprintf('Estado del puerto %s\n', PuertoSerial.Status);
   % -------- LEER READY --------
   if PuertoSerial.BytesAvailable > 0
       ready = strtrim(fgetl(PuertoSerial));
       fprintf('Arduino ? %s\n', ready);
   end
   % -------- PING / PONG --------
   fprintf(PuertoSerial,'PING\n');
   pong = strtrim(fgetl(PuertoSerial));
   if ~strcmp(pong,'PONG')
       fclose(PuertoSerial); delete(PuertoSerial);
       error('Arduino no responde "PONG"');
   end
   %fprintf('PING OK\n');
   fprintf('Comunicacion ARDUINO-MATLAB: OK!\n');

   
   %fprintf('Movimiento y adquisici�n finalizados OK\n');

    % -------- CIERRE --------
    %fclose(s);
    %delete(s);
    %clear s;

    %fprintf('Puerto serial cerrado\n');
    
    %save('medicion_luz.mat','data')
    %fprintf('Medicion grabada en archivo .mat\n');
    
    
%figure
%plot(data.angulo, data.adc, 'o-')
%xlabel('�ngulo (�)')
%ylabel('ADC')
%grid on
end