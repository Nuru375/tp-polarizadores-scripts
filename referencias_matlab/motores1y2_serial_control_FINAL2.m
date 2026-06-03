function data = motores1y2_serial_control_FINAL2(PuertoSerial,MOT1ang_i, MOT1ang_f, MOT1paso, MOT1sentido,MOT2ang_i, MOT2ang_f, MOT2paso, MOT2sentido)
% Control de motor paso a paso vía Arduino + adquisición ADC + Drivers
% A4988 (MOTOR1) y DVR8825 (MOTOR 2)
% Protocolo: motor|ang_i|ang_f|paso|sentido\n
% motor: 1 o 2
%ang_i: en grados
%ang_f: en grados
%paso: en grados
%sentido: 'H' (Horario) o 'A' (antihorario)
% Baudrate: 19200

% Devuelve estructura "data" con los datos medidos
% DATA enviada por Arduino:
% DATA|motor|index|angulo_deg|adc

% Resolucion de los motores
resMot1 = 360 / 2000; %0.18°/micropaso
resMot2 = 360 / 2300; %0.156°/micropaso

% -------- Conversion de grados a MICROpasos --------

MOT1ang_i = round(MOT1ang_i / resMot1);
MOT1ang_f = round(MOT1ang_f / resMot1);
MOT1paso = round(MOT1paso / resMot1);

MOT2ang_i = round(MOT2ang_i / resMot2);
MOT2ang_f = round(MOT2ang_f / resMot2);
MOT2paso = round(MOT2paso / resMot2);


% -------- INICIALIZAR ESTRUCTURA --------
data.motor  = [];
data.index  = [];
data.angulo = [];
data.adc    = [];

%-------------  ANGULO INICIAL DEL MOTOR 1 Y DEL MOTOR 2   ----------------
% -------- COMANDO para el MOTOR 1--------
cmd = sprintf('%d|%.2f|%.2f|%.2f|%s',1, MOT1ang_i, 0, 0, MOT1sentido);
fprintf('MOTOR 1: Matlab-->Arduino: %s\n', cmd);
fprintf(PuertoSerial,'%s\n',cmd);
% -------- ESPERAR ACK --------
while true
    line = strtrim(fgetl(PuertoSerial));
    %fprintf('MOTOR1: Arduino ? %s\n', line);
    if strcmp(line,'ACK')
        break;
    elseif strncmp(line,'ERR',3)
        fclose(PuertoSerial); delete(PuertoSerial);
        error('MOTOR1: Arduino devolvió ERR');
    end
end
% -------- LEER DATA HASTA "DONE" --------
while true
    if PuertoSerial.BytesAvailable == 0
        pause(0.01);
        continue
    end
    line = strtrim(fgetl(PuertoSerial));
    % ---- DONE ----
    if strcmp(line,'DONE')
        break
    end
    % ---- DATA ----
    if strncmp(line,'DATA',4)
        tokens = strsplit(line,'|');
        data.motor(end+1)  = str2double(tokens{2});
        data.index(end+1)  = 0;
        data.angulo(end+1) = round(MOT1ang_i*resMot1,2);%str2double(tokens{4})
        data.adc(end+1)    = nan;%str2double(tokens{5});
        lectura = sprintf('%s %d | %.2f | %.2f ','# MOTOR|ANGULO(°)|SENSOR: ',data.motor(end), data.angulo(end), data.adc(end));
        fprintf('LECTURA (MOTOR 1): %s\n', lectura);
    end
    % ---- ERROR ----
    if strncmp(line,'ERR',3)
        fclose(PuertoSerial); delete(PuertoSerial);
        error('MOTOR1: Error enviado por Arduino');
    end
end



% -------- COMANDO para el MOTOR 2--------
cmd = sprintf('%d|%.2f|%.2f|%.2f|%s',2, MOT2ang_i, 0, 0, MOT2sentido);
fprintf('MOTOR 2: Matlab-->Arduino: %s\n', cmd);
fprintf(PuertoSerial,'%s\n',cmd);
% -------- ESPERAR ACK --------
while true
    line = strtrim(fgetl(PuertoSerial));
    %fprintf('MOTOR 2: Arduino ? %s\n', line);
    if strcmp(line,'ACK')
        break;
    elseif strncmp(line,'ERR',3)
        fclose(PuertoSerial); delete(PuertoSerial);
        error('MOTOR 2: Arduino devolvió ERR');
    end
end
% -------- LEER DATA HASTA "DONE" --------
while true
    if PuertoSerial.BytesAvailable == 0
        pause(0.01);
        continue
    end
    line = strtrim(fgetl(PuertoSerial));
    % ---- DONE ----
    if strcmp(line,'DONE')
        break
    end
    % ---- DATA ----
    if strncmp(line,'DATA',4)
        tokens = strsplit(line,'|');
        data.motor(end+1)  = str2double(tokens{2});
        data.index(end+1)  = 0;
        data.angulo(end+1) = round(MOT2ang_i*resMot2,2);%str2double(tokens{4})
        data.adc(end+1)    = str2double(tokens{5});
        lectura = sprintf('%s %d | %.2f | %.2f ','# MOTOR|ANGULO(°)|SENSOR: ',data.motor(end), data.angulo(end), data.adc(end));
        fprintf('LECTURA (MOTOR 2): %s\n', lectura);
    end
    % ---- ERROR ----
    if strncmp(line,'ERR',3)
        fclose(PuertoSerial); delete(PuertoSerial);
        error('MOTOR 2: Error enviado por Arduino');
    end
end
%--------------------------------------------------------------------------





MOT1numexp = round((MOT1ang_f - MOT1ang_i) / MOT1paso);

if MOT1numexp < 1
    fprintf('MOTOR 1: Movimiento y adquisición finalizados: MOT1numexp < 1\n');
    return;
elseif isnan(MOT1numexp) || isinf(MOT1numexp)
    MOT1numexp = 1;
end

MOT2numexp = round((MOT2ang_f - MOT2ang_i) / MOT2paso);

if MOT2numexp < 1
    fprintf('MOTOR 2: Movimiento y adquisición finalizados: MOT2numexp < 1\n');
    return;
elseif isnan(MOT2numexp) || isinf(MOT2numexp)
    MOT2numexp = 1;
end



for i = 1: MOT1numexp + 1
    for j = 1: MOT2numexp
        % -------- COMANDO --------
        cmd = sprintf('%d|%.2f|%.2f|%.2f|%s',2, 0, 0, MOT2paso, MOT2sentido);
        fprintf('MOTOR 2: Matlab-->Arduino: %s\n', cmd);
        fprintf(PuertoSerial,'%s\n',cmd);
        % -------- ESPERAR ACK --------
        while true
            line = strtrim(fgetl(PuertoSerial));
            %fprintf('MOTOR 2: Arduino ? %s\n', line);
            if strcmp(line,'ACK')
                break;
            elseif strncmp(line,'ERR',3)
                fclose(PuertoSerial); delete(PuertoSerial);
                error('MOTOR 2: Arduino devolvió ERR');
            end
        end
        % -------- LEER DATA HASTA "DONE" --------
        while true
            if PuertoSerial.BytesAvailable == 0
                pause(0.01);
                continue
            end
            line = strtrim(fgetl(PuertoSerial));
            % ---- DONE ----
            if strcmp(line,'DONE')
                break
            end
            % ---- DATA ----
            if strncmp(line,'DATA',4)
                tokens = strsplit(line,'|');
                data.motor(end+1)  = str2double(tokens{2});
                data.index(end+1)  = j;%str2double(tokens{3});
                %switch str2num(tokens{2})
                %case{1}
                %    data.angulo(end+1) = round(data.angulo(end) + 1*paso*resMot1,2);%str2double(tokens{4})
                %case{2}
                
                %data.angulo(end+1) = round(data.angulo(end) + 1*MOT2paso*resMot2,2);%str2double(tokens{4})
                data.angulo(end+1) = round(MOT2ang_i*resMot2,2) + j * round(MOT2paso*resMot2,2);%round(data.angulo(end) + 1*MOT2paso*resMot2,2);%str2double(tokens{4})
                
                %otherwise
                %    disp('No sabe si es MOTOR 1 o MOTOR 2')
                %end
                %data.angulo(end+1) = round(data.angulo(end) + 1*paso*resMot1,2);
                
                data.adc(end+1)    = str2double(tokens{5});
                lectura = sprintf('%s %d | %.2f | %.2f ','# MOTOR|ANGULO(°)|SENSOR: ',data.motor(end), data.angulo(end), data.adc(end));
                fprintf('MOTOR 2: LECTURA: %s\n', lectura);
            end
            % ---- ERROR ----
            if strncmp(line,'ERR',3)
                fclose(PuertoSerial); delete(PuertoSerial);
                error('MOTOR 2: Error enviado por Arduino');
            end
        end
    end
    if  i ~= (MOT1numexp + 1)
    % -------- COMANDO MOTOR 1--------
        cmd = sprintf('%d|%.2f|%.2f|%.2f|%s',1, 0, 0, MOT1paso, MOT1sentido);
        fprintf('MOTOR 1: Matlab-->Arduino: %s\n', cmd);
        fprintf(PuertoSerial,'%s\n',cmd);
        % -------- ESPERAR ACK --------
        while true
            line = strtrim(fgetl(PuertoSerial));
            %fprintf('MOTOR 1: Arduino ? %s\n', line);
            if strcmp(line,'ACK')
                break;
            elseif strncmp(line,'ERR',3)
                fclose(PuertoSerial); delete(PuertoSerial);
                error('MOTOR 1: Arduino devolvió ERR');
            end
        end
        % -------- LEER DATA HASTA "DONE" --------
        while true
            if PuertoSerial.BytesAvailable == 0
                pause(0.01);
                continue
            end
            line = strtrim(fgetl(PuertoSerial));
            % ---- DONE ----
            if strcmp(line,'DONE')
                break
            end
            % ---- DATA ----
            if strncmp(line,'DATA',4)
                tokens = strsplit(line,'|');
                data.motor(end+1)  = str2double(tokens{2});
                data.index(end+1)  = i;%str2double(tokens{3});
                %switch str2num(tokens{2})
                %case{1}
                %    data.angulo(end+1) = round(data.angulo(end) + 1*paso*resMot1,2);%str2double(tokens{4})
                %case{2}
                
                %data.angulo(end+1) = round(data.angulo(end) + 1*MOT1paso*resMot1,2);%str2double(tokens{4})
                data.angulo(end+1) = round(MOT1ang_i*resMot1,2) + i * round(MOT1paso*resMot1,2);%round(data.angulo(end-data.index(end-1)) + 1*MOT1paso*resMot1,2);%str2double(tokens{4})
                %otherwise
                %    disp('No sabe si es MOTOR 1 o MOTOR 2')
                %end
                %data.angulo(end+1) = round(data.angulo(end) + 1*paso*resMot1,2);
                
                data.adc(end+1)    = str2double(tokens{5});
                lectura = sprintf('%s %d | %.2f | %.2f ','# MOTOR|ANGULO(°)|SENSOR: ',data.motor(end), data.angulo(end), data.adc(end));
                fprintf('MOTOR 1: LECTURA: %s\n', lectura);
            end
            % ---- ERROR ----
            if strncmp(line,'ERR',3)
                fclose(PuertoSerial); delete(PuertoSerial);
                error('MOTOR 1: Error enviado por Arduino');
            end
        end
end
end


fprintf('Movimiento y adquisición finalizados OK\n');

% -------- CIERRE --------
%fclose(s);
%delete(s);
%clear s;

%fprintf('Puerto serial cerrado\n');

%save('medicion_luz.mat','data')
%fprintf('Medicion grabada en archivo .mat\n');


%figure
%plot(data.angulo, data.adc, 'o-')
%xlabel('Ángulo (°)')
%ylabel('ADC')
%grid on
end