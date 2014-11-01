function DA= Dagostino(X)
	#f = fopen('data.txt');   
	#g = textscan(f,'%f%[^\n\r]')
	#fclose(f)
	Xs= sort(X);
	N= length(X);
	I= 1:N;
	vec=(I-(N+1)/2).*Xs;
	T= sum(vec);
	DA=T./(std(X,1)*N.^2);


# rango para n=30 0.2693 0.2861
	#for i=1:length(g{1,1})
	#  NVar{i} = gdat(i, :);
	#end
endfunction
