# Source of documentation here: https://developer.ibm.com/tutorials/l-rpm1/

%define name            opsconf

Name:           %{name}
Version:        %{version} 
Release:        %{release}%{?dist}
Summary:        CNES' Opsconf

License:        MIT
URL:            https://gitlab.cnes.fr/DNO-OP/opsconf 
Source:         %{name}-%{version}.tar.gz
BuildArch:      noarch


Prefix: 	/usr
BuildRequires:  git
Requires:       git
Requires: 	bash

%description
Operational data configuration management tool

%prep
%setup -q

%build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{prefix}/bin
cp -rf src/bin/* $RPM_BUILD_ROOT/%{prefix}/bin/
mkdir -p $RPM_BUILD_ROOT/%{prefix}/share/opsconf/
cp -rf src/share/* $RPM_BUILD_ROOT/%{prefix}/share/opsconf/


%files
%defattr(-,root,root,-)
%doc
%{prefix}/bin/opsconf
%{prefix}/share/opsconf/githooks/commit-msg
%{prefix}/share/opsconf/githooks/post-commit
%{prefix}/share/opsconf/githooks/pre-commit
%{prefix}/share/opsconf/libs/libopsconf
%{prefix}/share/opsconf/opsconf-checkout
%{prefix}/share/opsconf/opsconf-commit
%{prefix}/share/opsconf/opsconf-diff
%{prefix}/share/opsconf/opsconf-init
%{prefix}/share/opsconf/opsconf-liststates
%{prefix}/share/opsconf/opsconf-log
%{prefix}/share/opsconf/opsconf-qualify
%{prefix}/share/opsconf/opsconf-rollback
%{prefix}/share/opsconf/opsconf-sync
%{prefix}/share/opsconf/opsconf-tag
%{prefix}/share/opsconf/opsconf-validate


%changelog
