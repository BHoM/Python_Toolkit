FROM python:3.10-slim
COPY . /Python_Toolkit

#requires build argument --build-context bhom-assemblies C:/ProgramData/BHoM/Assemblies
COPY --from=bhom-assemblies . /bin/BHoM/Assemblies

#install .net core 8.0, and set the pythonnet runtime to the .net core CLR
RUN apt-get update \
	&& apt-get install -y wget
	
RUN wget https://packages.microsoft.com/config/debian/13/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN rm packages-microsoft-prod.deb

RUN apt-get update \
	&& apt-get install -y aspnetcore-runtime-10.0

ENV PYTHONNET_RUNTIME="coreclr"

RUN pip3 install ./Python_Toolkit

RUN rm ./Python_Toolkit -rf